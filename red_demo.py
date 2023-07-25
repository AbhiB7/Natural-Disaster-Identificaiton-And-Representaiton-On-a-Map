import random
import customtkinter
import pandas as pd
from tkintermapview import TkinterMapView
import tweepy
import tkintermapview as tkm
from tkinter import *
from geopy.geocoders import Nominatim
import pickle
import math
import datetime


customtkinter.set_default_color_theme("blue")


class App(customtkinter.CTk):
    APP_NAME = "TkinterMapView with CustomTkinter"
    WIDTH = 800
    HEIGHT = 500

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title(App.APP_NAME)
        self.geometry(str(App.WIDTH) + "x" + str(App.HEIGHT))
        self.minsize(App.WIDTH, App.HEIGHT)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.bind("<Command-q>", self.on_closing)
        self.bind("<Command-w>", self.on_closing)
        self.createcommand('tk::mac::Quit', self.on_closing)

        self.marker_list = []
        customtkinter.set_appearance_mode("dark")
        # ============ create two CTkFrames ============

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.frame_left = customtkinter.CTkFrame(master=self, width=150, corner_radius=0, fg_color=None)
        self.frame_left.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")

        self.frame_right = customtkinter.CTkFrame(master=self, corner_radius=0)
        self.frame_right.grid(row=0, column=1, rowspan=1, pady=0, padx=0, sticky="nsew")

        self.frame_bot= customtkinter.CTkFrame(master=self, corner_radius=0, fg_color= "green")
        self.frame_bot.grid(row=1, column=0, padx=0, pady=0, columnspan= 2,  sticky="nsew")
        # ============ frame_left ============

        self.frame_left.grid_rowconfigure(2, weight=1)

        self.button_1 = customtkinter.CTkButton(master=self.frame_left,
                                                text="Set Marker",
                                                command=self.set_marker_event)
        self.button_1.grid(pady=(20, 0), padx=(20, 20), row=0, column=0)

        self.button_2 = customtkinter.CTkButton(master=self.frame_left,
                                                text="Clear Markers",
                                                command=self.clear_marker_event)
        self.button_2.grid(pady=(20, 0), padx=(20, 20), row=1, column=0)

        self.value_inside= customtkinter.StringVar(value="SVC")  # set initial value

        self.model_ops_list=["BERT", "SVC"]
        # self.drop = customtkinter.CTkOptionMenu(self.frame_left, self.value_inside, *self.model_ops_list )
        self.drop= customtkinter.CTkOptionMenu(master=self.frame_left,
                                       values=["BERT", "SVC"],
                                    #    command=optionmenu_callback,
                                       variable= self.value_inside)
        self.drop.grid(pady=(20, 0), padx=(20, 20), row=2, column=0)


        self.map_label = customtkinter.CTkLabel(self.frame_left, text="Tile Server:", anchor="w")
        self.map_label.grid(row=3, column=0, padx=(20, 20), pady=(20, 0))
        self.map_option_menu = customtkinter.CTkOptionMenu(self.frame_left, values=["OpenStreetMap", "Google normal", "Google satellite"],
                                                                       command=self.change_map)
        self.map_option_menu.grid(row=4, column=0, padx=(20, 20), pady=(10, 40))


        # self.appearance_mode_label = customtkinter.CTkLabel(self.frame_left, text="Appearance Mode:", anchor="w")
        # self.appearance_mode_label.grid(row=5, column=0, padx=(20, 20), pady=(20, 0))
        # self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.frame_left, values=["Light", "Dark", "System"],
        #                                                                command=self.change_appearance_mode)
        # self.appearance_mode_optionemenu.grid(row=6, column=0, padx=(20, 20), pady=(10, 20))

        # ============ frame_right ============

        self.frame_right.grid_rowconfigure(1, weight=1)
        self.frame_right.grid_rowconfigure(0, weight=0)
        self.frame_right.grid_columnconfigure(0, weight=1)
        self.frame_right.grid_columnconfigure(1, weight=0)
        self.frame_right.grid_columnconfigure(2, weight=1)

        self.map_widget = TkinterMapView(self.frame_right, corner_radius=0)
        self.map_widget.grid(row=1, rowspan=1, column=0, columnspan=3,
                             sticky="nswe", padx=(0, 20), pady=(0, 20))
        self.map_widget.add_right_click_menu_command(label="Add Marker",
                                                command=self.add_marker_event,
                                                pass_coords=True)

        self.entry = customtkinter.CTkEntry(master=self.frame_right,
                                            placeholder_text="type address")
        self.entry.grid(row=0, column=0, sticky="we", padx=(12, 0), pady=12)
        self.entry.bind("<Return>", self.search_event)

        self.button_5 = customtkinter.CTkButton(master=self.frame_right,
                                                text="Search",
                                                width=90,
                                                command=self.search_event)
        self.button_5.grid(row=0, column=1, sticky="w", padx=(12, 0), pady=12)

        # Set default values
        self.map_widget.set_address("Mumbai")
        self.map_option_menu.set("OpenStreetMap")

        # configure grid system
        # self.grid_rowconfigure(0, weight=1)
        # self.grid_columnconfigure(0, weight=1)
        self.textbox = customtkinter.CTkTextbox(master=self.frame_bot,
                                                width=800,
                                                corner_radius=0
                                                )
        self.textbox.grid(row=0, column=0, sticky = "nsew")
        #0.0 means enter at line 0 character 0
        # self.textbox.insert("0.0", "Some example text!\n" * 50)        #textbox to display tweets

    #================= setting up twitter api =======================
        self.ACCESS_TOKEN = '1574425806545117184-7A5qOM7dRe5UjCCuUVdzjbmuhOeICr'
        self.ACCESS_SECRET = 'lyz9sy828kUYX0c2429lce4eCjFJR0RHKx0189BczBczz'
        self.CONSUMER_KEY = 'qkBxRRYAv1KGXLLQqg6FkzlP4'
        self.CONSUMER_SECRET = '3rAK403gUYnKAmccEO2sQOKjnakjZuPS9uyQZ97UZuSrnalAUi'


        # Create API object
        self.api = self.connect_to_twitter_OAuth()
#==========================all the funcitons+======================

    def prediction(self, to_be_classified):
        print(self.value_inside.get())
        if self.value_inside.get() == "SVC":
            self.filename = 'text_clf.sav'
            self.loaded_model = pickle.load(open(self.filename, 'rb'))
        elif self.value_inside.get() == "BERT":
            import os
            os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
            import tensorflow as tf
            import tensorflow_hub as hub
            import tensorflow_text as text
            from sklearn.model_selection import train_test_split
            print('Tensorflow module imported')
            self.loaded_model = tf.keras.models.load_model('/Major_Project/models/bert_success_1/bert_success_1')
        else:
            self.filename = 'text_clf.sav'
            self.loaded_model = pickle.load(open(self.filename, 'rb'))

        self.predictions = self.loaded_model.predict(self.to_be_classified)
        print(f"\n\n {self.loaded_model.predict(self.to_be_classified)}")
        self.disaster = 0 #count number of disaster events
        for i in self.predictions:
            if i:
                self.disaster +=1
        self.dis_cond = self.disaster / len(self.predictions)
        print(self.dis_cond)
        if self.dis_cond > 0.55:
            return 1
        else:
            return 0
        # Setup access to API
    def connect_to_twitter_OAuth(self):
        self.auth = tweepy.OAuthHandler(self.CONSUMER_KEY, self.CONSUMER_SECRET)
        self.auth.set_access_token(self.ACCESS_TOKEN, self.ACCESS_SECRET)
        self.api = tweepy.API(self.auth)
        return self.api
    def search_event(self, event=None):
        self.map_widget.set_address(self.entry.get())
    def find_tweet(self, coords):
#         self.to_be_classified = []#this is going to be passed ahead
#         self.coord_str = str(coords[0]) + ", " + str(coords[1])
#         print("cordinates are: ", coords)
#         self.geolocator = Nominatim(user_agent="MyApp")
#         # Latitude & Longitude input
#         self.coordinates = self.coord_str
#         self.location = self.geolocator.reverse(self.coordinates)
#         self.address = self.location.raw['address']
#         # Traverse the data
#         self.city = self.address.get('city', '')
#         self.state = self.address.get('state', '')
#         self.country = self.address.get('country', '')
#         print(f"{self.city} \n{self.state} \n{self.country} \n")
#         places = self.api.search_geo(lat = coords[0], long = coords[1], granularity="city")
#         # for place in places:
#         #     print("placeid:%s" % place)
#         placed = "placeid:%s" % places
#         #item iterator class
#         # start_date = datetime.datetime(2019, 8, 8, 12, 00, 00)
#         # end_date = datetime.datetime(2019, 8, 10, 13, 00, 00)
#         # self.public_tweets = tweepy.Cursor(self.api.search_tweets, count=5,q="place:%s" % places[0].id, tweet_mode="extended", lang = "en",  until = end_date).items(50)
#         # for tweet in self.public_tweets:
#         #     self.to_be_classified.append(tweet.full_text)
#         #     print("result of the find tweet function", tweet.full_text)
#         df = pd.read_csv("F:\Major_Project\kerala_flood_nepal_earthquake_english_only.csv")
#         self.to_be_classified = df.tweet.to_list()
#         print(self.to_be_classified)
        df = pd.read_csv("kerala_flood_nepal_earthquake_english_only.csv")
        self.to_be_classified = df["tweet"].to_list()
        random.shuffle(self.to_be_classified)
        return self.to_be_classified[:100]

    def define_poly(self, coords):
        self.deg = 0
        self.pol_arr = []
        while self.deg < 2*math.pi:# in the form [()]
            self.pol_arr.append((coords[0] + (0.01*math.cos(self.deg)), coords[1] + (0.01*math.sin(self.deg))))
            self.deg = self.deg + (2*math.pi/360)
        return self.pol_arr

    def set_marker_event(self):
        current_position = self.map_widget.get_position()
        self.marker_list.append(self.map_widget.set_marker(current_position[0], current_position[1]))

    def clear_marker_event(self):
        for marker in self.marker_list:
            marker.delete()

    def add_marker_event(self, coords):
    #     global to_be_classified
        print("Add marker:", coords)
        self.new_marker = self.map_widget.set_marker(coords[0], coords[1], text="new marker")
        self.poly = []
        self.poly = self.define_poly(coords)
    #     print(new_marker.position, new_marker.text)  # get position and text
        self.to_be_classified = self.find_tweet(coords)
        self.line_counter = 0
        for i in range (len(self.to_be_classified)):
            self.textbox.insert((str(self.line_counter)+".0"),str(self.to_be_classified[i]))        #textbox to display tweets
            self.line_counter += 1
            self.textbox.insert((str(self.line_counter)+".0"),"\n")        #textbox to display tweets
            self.line_counter += 1

        self.pred_condition = self.prediction(self.to_be_classified)
        # self.pred_condition = False
        if self.pred_condition:
            self.polygon_1 = self.map_widget.set_polygon(self.poly, fill_color= "red", outline_color="red", name="disaster_affected_area")
        else:
            self.polygon_1 = self.map_widget.set_polygon(self.poly, outline_color="green", name="disaster_affected_area")

        # print(f"\n\n {to_be_classified}")

    # def change_appearance_mode(self, new_appearance_mode: str):
    #     customtkinter.set_appearance_mode(new_appearance_mode)

    def change_map(self, new_map: str):
        if new_map == "OpenStreetMap":
            self.map_widget.set_tile_server("https://a.tile.openstreetmap.org/{z}/{x}/{y}.png")
        elif new_map == "Google normal":
            self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
        elif new_map == "Google satellite":
            self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)

    def on_closing(self, event=0):
        self.destroy()

    def start(self):
        self.mainloop()


if __name__ == "__main__":
    app = App()
    app.start()

