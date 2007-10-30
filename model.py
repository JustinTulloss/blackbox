#!/usr/bin/python
#
# Justin Tulloss
# 
# Much of this code was blatantly copied from
# the example code in the PythonDaap library

"""Module to aggregate every DAAP service we can find"""

from daap import DAAPClient
import gtk
import gobject
import dbus
import avahi
import dbus.glib

class MusicData(gtk.Widget):

    #signals that indicate that you should probably update your view
    __gsignals__ = dict(
                add_tracks=(gobject.SIGNAL_RUN_FIRST,
                      gobject.TYPE_NONE,()),
                remove_tracks=(gobject.SIGNAL_RUN_FIRST,
                      gobject.TYPE_NONE,()))

    class DaapData(object):
        client = None
        session = None
        database = None

    _tracks = []

    def __init__(self):
        """Make a new music data provider."""
        super(MusicData, self).__init__()

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
        print "Found service '%s' of type '%s' in domain '%s' at address '%s:%s'" % (name, type, domain, address, port)
        self.add_server(address)
        gobject.idle_add(self.emit, "add_tracks")

    def _remove_service(self, interface, protocol, name, type, domain):
        pass

    def add_server(self, ip, port=3689):
        sd = self.DaapData()
        nc = DAAPClient()

        nc.connect(ip, port)
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
    
    def query(self, filters={}):
        """Finds a list of songs that match the 
        arbitrary number of filters passed in"""
        def ffunc(track):
            """Filter function goes through each filter condition and
            sees if the DAAPTrack matches"""
            match = True
            for key in filters.keys():
                if not getattr(track, key) == filters[key]:
                    return False
            return True

        return filter(ffunc, self._tracks)


if __name__=="__main__":
    import gobject
    md = MusicData()
    gobject.MainLoop().run()
