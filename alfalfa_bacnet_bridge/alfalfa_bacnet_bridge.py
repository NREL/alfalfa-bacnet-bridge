from datetime import datetime
import logging
import math
import sys
import os
from bacpypes.app import BIPSimpleApplication
from bacpypes.core import deferred, run
from bacpypes.debugging import bacpypes_debugging, ModuleLogger
from bacpypes.local.device import LocalDeviceObject
from bacpypes.object import AnalogInputObject, register_object_type
from bacpypes.local.object import AnalogValueCmdObject
from bacpypes.task import recurring_function
from alfalfa_client.alfalfa_client import AlfalfaClient
from alfalfa_client.alfalfa_client import RunID
from bacpypes.service.device import DeviceCommunicationControlServices
from bacpypes.service.object import ReadWritePropertyMultipleServices
from bacpypes.primitivedata import CharacterString, Date, Time
from bacpypes.basetypes import DeviceStatus

_debug = 0
_log = ModuleLogger(globals())

logger = logging.getLogger("AlfalfaBACnetBridge")
logger.setLevel(logging.DEBUG)
log_formatter = logging.Formatter('%(asctime)s - %(threadName)s - %(levelname)s - %(message)s')

stdout_handler = logging.StreamHandler()
stdout_handler.setLevel(logging.DEBUG)
stdout_handler.setFormatter(log_formatter)

file_handler = logging.FileHandler('bridge.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(log_formatter)

logger.addHandler(stdout_handler)
logger.addHandler(file_handler)

@bacpypes_debugging
class AlfalfaBACnetApplication(BIPSimpleApplication,
                            ReadWritePropertyMultipleServices,
                            DeviceCommunicationControlServices,):
    pass

class AlfalfaBACnetDevice(LocalDeviceObject):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._date_time: datetime = None

    def ReadProperty(self, propid, arrayIndex=None):
        if propid == "localTime" and self._date_time != None:
            time = Time(str(self._date_time.time()))
            return time.value
        if propid == "localDate" and self._date_time != None:
            date = Date(str(self._date_time.date()))
            return date.value
        return super().ReadProperty(propid, arrayIndex)

@bacpypes_debugging
@register_object_type(vendor_id=555)
class LocalAnalogValueObject(AnalogValueCmdObject):
    def __init__(self, sim_value, **kwargs):
        super().__init__(**kwargs)
        self._sim_value = sim_value

    def ReadProperty(self, propid, arrayIndex=None):
        if propid == "presentValue":
            return self._sim_value
        return super().ReadProperty(propid, arrayIndex)

class AlfalfaBACnetBridge():

    def __init__(self, host, run_id: RunID) -> None:
        self.client = AlfalfaClient(host)

        self.run_id = run_id

        self.device = AlfalfaBACnetDevice(
        objectName=os.getenv("ALFALFA_DEVICE_NAME","AlfalfaProxy"),
        objectIdentifier=int(os.getenv("ALFALFA_DEVICE_ID", 599)),
        maxApduLengthAccepted=int(1024),
        segmentationSupported="segmentedBoth",
        vendorIdentifier=555,
        vendorName=CharacterString("NREL"),
        modelName=CharacterString("Alfalfa BACnet Bridge"),
        systemStatus=DeviceStatus(1),
        description=CharacterString("BACpypes (Python) based tool for exposing alfalfa models to real world BAS systems via BACnet"),
        firmwareRevision="0.0.0",
        applicationSoftwareVersion="0.0.0",
        protocolVersion=1,
        protocolRevision=0)

        self.application = AlfalfaBACnetApplication(self.device, "0.0.0.0")

        self.points = {}

    def setup_points(self):
        inputs = self.client.get_inputs(self.run_id)
        inputs.sort()
        outputs = self.client.get_outputs(self.run_id)
        output_names = list(outputs.keys())
        output_names.sort()

        index = 0

        for input in inputs:
            if input in outputs:
                self.points[input] = LocalAnalogValueObject(objectName=input, objectIdentifier=("analogValue", index), sim_value=outputs[input])
                logger.info(f"Creating BIDIRECTIONAL point: '{input}'")
            else:
                self.points[input] = AnalogValueCmdObject(objectName=input, objectIdentifier=("analogValue", index))
                logger.info(f"Creating INPUT point: '{input}'")
            self.points[input]._had_value = False
            index += 1

        for output in output_names:
            if output in self.points:
                continue
            self.points[output] = AnalogInputObject(objectName=output, objectIdentifier=("analogInput", index), presentValue=outputs[output])
            logger.info(f"Creating OUTPUT point: '{output}'")
            index += 1

        for point in self.points.values():
            self.application.add_object(point)



    def run(self):
        @recurring_function(1000)
        @bacpypes_debugging
        def main_loop():
            try:
                inputs = self.client.get_inputs(self.run_id)
                outputs = self.client.get_outputs(self.run_id)

                sim_time = self.client.get_sim_time(self.run_id)
            except Exception as e:
                logger.error(e)
                return
            self.device._date_time = sim_time

            set_inputs = {}
            for point, object in self.points.items():
                if point in outputs:
                    if isinstance(object, LocalAnalogValueObject):
                        object._sim_value = outputs[point]
                    else:
                        object.presentValue = outputs[point]
                if point in inputs:
                    current_value, value_type = object._highest_priority_value()
                    if value_type is not None:
                        if math.isfinite(current_value):
                            set_inputs[point] = current_value
                            object._had_value = True
                        else:
                            logger.warn(f"Got non-finite value {current_value} for point {point}")
                    elif object._had_value:
                        set_inputs[point] = None
                        object._had_value = False
            if len(set_inputs) > 0:
                try:
                    self.client.set_inputs(self.run_id, set_inputs)
                except Exception as e:
                    logger.error(e)


        deferred(main_loop)
        run()

if __name__ == "__main__":
    run_id = sys.argv[2]
    host = sys.argv[1]
    bridge = AlfalfaBACnetBridge(host, run_id)
    bridge.setup_points()
    bridge.run()
