import os
from bacpypes.app import BIPSimpleApplication
from bacpypes.core import deferred, run
from bacpypes.debugging import bacpypes_debugging, ModuleLogger
from bacpypes.local.device import LocalDeviceObject
from bacpypes.consolelogging import ConfigArgumentParser
from bacpypes.object import AnalogInputObject, register_object_type
from bacpypes.local.object import AnalogValueCmdObject
from bacpypes.task import recurring_function
from alfalfa_client.alfalfa_client import AlfalfaClient
from alfalfa_client.alfalfa_client import SiteID
from bacpypes.service.device import DeviceCommunicationControlServices
from bacpypes.service.object import ReadWritePropertyMultipleServices

_debug = 0
_log = ModuleLogger(globals())

@bacpypes_debugging
class AlfalfaBACnetApplication(BIPSimpleApplication,
                            ReadWritePropertyMultipleServices,
                            DeviceCommunicationControlServices,):
    pass



@bacpypes_debugging
@register_object_type(vendor_id=999)
class LocalAnalogValueObject(AnalogValueCmdObject):
    def __init__(self, sim_value, **kwargs):
        super().__init__(**kwargs)
        self._sim_value = sim_value

    def ReadProperty(self, propid, arrayIndex=None):
        if propid == "presentValue":
            return self._sim_value
        return super().ReadProperty(propid, arrayIndex)

class AlfalfaBACnetBridge():

    def __init__(self, host, site_id: SiteID) -> None:
        self.client = AlfalfaClient(host)
        self.site_id = site_id

        parser = ConfigArgumentParser(description=__doc__)

        args = parser.parse_args()

        self.device = LocalDeviceObject(ini=args.ini)
        self.application = AlfalfaBACnetApplication(self.device, "0.0.0.0")

        self.points = {}

    def setup_points(self):

        inputs = self.client.get_inputs(self.site_id)
        outputs = self.client.get_outputs(self.site_id)

        index = 0

        for input in inputs:
            if input in outputs:
                self.points[input] = LocalAnalogValueObject(objectName=input, objectIdentifier=("analogValue", index), sim_value=outputs[input])
            else:
                self.points[input] = AnalogValueCmdObject(objectName=input, objectIdentifier=("analogValue", index))
            index += 1

        for output, value in outputs.items():
            if output in self.points:
                continue
            self.points[output] = AnalogInputObject(objectName=output, objectIdentifier=("analogInput", index), presentValue=value) 
            index += 1

        for point in self.points.values():
            self.application.add_object(point)


    def run(self):
        @recurring_function(1000)
        @bacpypes_debugging
        def main_loop():
            inputs = self.client.get_inputs(self.site_id)
            outputs = self.client.get_outputs(site_id)


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
                        set_inputs[point] = current_value
            if len(set_inputs) > 0:
                self.client.set_inputs(site_id, set_inputs)
        
        deferred(main_loop)
        run()

if __name__ == "__main__":
    site_id = os.getenv('ALFALFA_SITE_ID')
    host = os.getenv('ALFALFA_HOST')
    bridge = AlfalfaBACnetBridge(host, site_id)
    bridge.setup_points()
    bridge.run()
