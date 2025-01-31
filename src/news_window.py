import gi
gi.require_version('Soup', '3.0')
from gi.repository import Adw
from gi.repository import Gtk,Soup,GLib,Gdk
import json
import os
import threading


class ImagePaint(Gtk.Widget):
    def __init__(self,parent,image_location,image_link,news_page_group,image_source_link):
        Gtk.Widget.__init__(self)
        self.parent            = parent
        self.image_link        = image_link
        self.image_location    = image_location
        self.news_page_group   = news_page_group
        self.image_source_link = image_source_link
        self.image_file        = None
        if os.path.exists(self.image_location):
            self.__texture   = Gdk.Texture.new_from_filename(self.image_location)
        else:
            self.__texture   = None
            self.download_image()

    def do_snapshot(self,snapshot):
        if self.__texture:
            self.__texture.snapshot(snapshot,self.parent.get_width(),self.parent.get_height())

    def do_get_request_mode(self):
        return Gtk.SizeRequestMode.CONSTANT_SIZE

    def do_measure(self, orientation, for_size):
        if orientation == Gtk.Orientation.HORIZONTAL:
            return (self.parent.get_width(), self.parent.get_width(), -1, -1)
        else:
            return (self.parent.get_height(),self.parent.get_height(), -1, -1)

    def download_image(self):
        try:
            self.session = Soup.Session.new()
            self.msg  = Soup.Message.new("GET",self.image_link)
            self.session.send_async(self.msg,GLib.PRIORITY_LOW,None,self.on_connect_finish,None)
        except Exception as e:
            print(e)

    def on_connect_finish(self,session, result, data):
        try:
            if self.msg.get_status() ==  Soup.Status.NOT_FOUND :
                return
            input_stream = session.send_finish(result)
            print(input_stream)
            input_stream.read_bytes_async(1024*500,GLib.PRIORITY_HIGH_IDLE  ,None,self.on_read_finish)
        except Exception as e:
            print(e)

    def on_read_finish(self,input_stream, result):
        try:
            chunk = input_stream.read_bytes_finish(result)
            if chunk.get_size()>0:
                if self.image_file == None:
                    self.image_file = open(self.image_location,"w+b")
                self.image_file.write(chunk.unref_to_data())
                input_stream.read_bytes_async(1024*500,GLib.PRIORITY_HIGH_IDLE  ,None,self.on_read_finish)
            else:
                self.image_file.close()
                input_stream.close()
                self.__texture = Gdk.Texture.new_from_filename(self.image_location)
                self.queue_draw()
                if self.image_source_link:
                    self.news_page_group.set_header_suffix(Gtk.LinkButton.new_with_label(self.image_source_link,"Picture Source"))

        except Exception as e:
            print(e)
            try:
                self.image_file.close()
                input_stream.close()
            except Exception as e:
                pass


class NewsGui():
    def __init__(self,parent,albasheer_news_data):
        self.parent              = parent
        self.albasheer_news_data = albasheer_news_data
        self.image_save_location = os.path.join(self.albasheer_news_data,"images")
        self.json_save_location  = os.path.join(self.albasheer_news_data,"news.json")
        self.news_window = Adw.PreferencesDialog.new()
        self.news_window.set_title(_("News"))
        self.news_page   =  Adw.PreferencesPage.new()
        self.news_window .add(self.news_page)
        self.news_page_group =  Adw.PreferencesGroup.new()
        self.news_page_group.set_size_request(-1, 400)
        self.news_page.add(self.news_page_group)
        self.get_news_info()

    def get_news_info(self):
        try:
            news_info_link = "https://raw.githubusercontent.com/yucefsourani/albasheer-electronic-quran-browser/refs/heads/master/news_info/news.json"
            self.session = Soup.Session.new()
            self.msg  = Soup.Message.new("GET",news_info_link)
            self.session.send_async(self.msg,GLib.PRIORITY_LOW,None,self.on_connect_finish,None)
        except Exception as e:
            print(e)

    def on_connect_finish(self,session, result, data):
        try:
            if self.msg.get_status() ==  Soup.Status.NOT_FOUND :
                return
            input_stream = session.send_finish(result)
            with open(self.json_save_location,"w+b") as json_f:
                json_f.write(b"")
            self.json_file = open(self.json_save_location,"a+b")
            input_stream.read_bytes_async(1024*500,GLib.PRIORITY_HIGH_IDLE  ,None,self.on_read_finish)
        except Exception as e:
            print(e)

    def on_read_finish(self,input_stream, result):
        try:
            chunk = input_stream.read_bytes_finish(result)
            if chunk.get_size()>0:
                self.json_file.write(chunk.unref_to_data())
                input_stream.read_bytes_async(1024*500,GLib.PRIORITY_HIGH_IDLE  ,None,self.on_read_finish)
            else:
                self.json_file.close()
                input_stream.close()
                with open(self.json_save_location,"r") as json_file:
                    info_ = json.load(json_file)
                self.read_info(info_)
        except Exception as e:
            try:
                self.json_file.close()
                input_stream.close()
            except Exception as e:
                pass
            print(e)

    def read_info(self,info_):
        image_l = os.path.join(self.image_save_location,info_["image"][0])
        image_info_link = f"https://raw.githubusercontent.com/yucefsourani/albasheer-electronic-quran-browser/refs/heads/master/news_info/{info_['image']}"
        image_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL,0)
        image_box.props.vexpand = True
        image_box.props.hexpand = True
        image_w = ImagePaint(image_box,image_l,image_info_link,self.news_page_group,info_["image"][1])
        image_box.append(image_w)
        self.news_page_group.add(image_box)
        if info_["title"]:
            self.news_page_group.set_title(info_["title"])
        if info_["body"]:
            text_view =  Gtk.TextView(cursor_visible=False,
                                      editable=False,
                                      wrap_mode=Gtk.WrapMode.WORD)
            text_view.get_buffer().set_text(info_["body"],-1)
            text_view.set_direction(Gtk.TextDirection.RTL)
            self.news_page_group.add(text_view)

        if info_["news_id"] != self.parent.app_settings.get_string("news-id"):
            self.parent.app_settings.set_string("news-id",info_["news_id"])
            GLib.timeout_add(2000,self.news_window.present,self.parent)

