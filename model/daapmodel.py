#!/usr/bin/python
#
# Justin Tulloss
# 
# Much of this code was blatantly copied from
# the example code in the PythonDaap library

"""Module to aggregate every DAAP service we can find"""

from daap import DAAPClient
from basemodel import BaseModel
import logging
import gobject
import dbus
import avahi
import dbus.glib

class DaapModel(BaseModel):

    class DaapData(object):
        client = None
        session = None
        database = None

    def __init__(self):
        """Make a new music data provider."""
        super(DaapModel, self).__init__()
        logging.basicConfig(level=logging.DEBUG)
        self._log = logging.getLogger(__name__)

        #### avahi discovery registration ####
        self._bus = dbus.SystemBus()
        self._server = dbus.Interface(
            self._bus.get_object(
                avahi.DBUS_NAME, 
                avahi.DBUS_PATH_SERVER
            ), 
            avahi.DBUS_INTERFACE_SERVER
        )

        stype = '_daap._tcp'
        domain = 'local'
        browser = dbus.Interface(
                self._bus.get_object(
                    avahi.DBUS_NAME, 
                    self._server.ServiceBrowserNew(
                        avahi.IF_UNSPEC, 
                        avahi.PROTO_UNSPEC, 
                        stype, 
                        domain, 
                        dbus.UInt32(0)
                    )
                ), 
                avahi.DBUS_INTERFACE_SERVICE_BROWSER
            )

        browser.connect_to_signal('ItemNew', self._new_service)
        browser.connect_to_signal('ItemRemove', self._remove_service)
        #### end of avahi discovery stuff ###

        self._servers = {}

    def _new_service(self, interface, protocol, name, type, domain, flags):
        interface, protocol, name, type, domain, host, aprotocol, address, port, txt, flags = self._server.ResolveService(
            interface, protocol, name, type, domain, 
            avahi.PROTO_UNSPEC, dbus.UInt32(0)
        )
        self._log.info("Found service '%s' of type '%s' in domain '%s' at address '%s:%s'",name, type, domain, address, port)
        self.add_server(address)
        gobject.idle_add(self.emit, "add_tracks")

    def _remove_service(self, interface, protocol, name, type, domain):
        pass

    def add_server(self, ip, port=3689):
        sd = self.DaapData()
        nc = DAAPClient()

        try:
            self._log.debug("Trying to connect to %s", ip)
            nc.connect(ip, port)
        except:
            self._log.warn("Could not connect to %s:%s", ip, port)
            return

        sd.session = nc.login()

        try:
            dbs = sd.session.databases()
        except:
            return #avoid problems with itunes 7 by ignoring them

        for db in dbs:
            if (str(db.id) == str(sd.session.library().id)):
                sd.database = db
                self._tracks.extend(db.tracks())

        self._servers[ip]=sd

    def remove_server(self, ip):
        bad = self._servers.pop(ip)
        bad.session.logout()
		#TODO:remove from the tracks listing
    
if __name__=="__main__":
    import gobject
    md = DappModel()
    gobject.MainLoop().run()
