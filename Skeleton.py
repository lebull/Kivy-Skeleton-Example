import kivy
kivy.require('1.8.0')

from kivy.app import App

from kivy.uix.popup import Popup
from kivy.uix.button import Button

from kivy.uix.stacklayout import StackLayout

from kivy.uix.screenmanager import ScreenManager, Screen

from kivy.properties import ObjectProperty, StringProperty, ListProperty, BooleanProperty

from kivySapService import KivySapService

import time #Used to generate random screen names.
import os.path

import logging

#TODO: Not sure how to handle importing the kv file if this is a module.

#======================================================
#   Login Screen
#======================================================
class LoginScreen(Screen):

    def onLoginAttempt(self):
        username = self.ids.UsernameInput.text
        password = self.ids.PasswordInput.text

        #Call the login function of the root app.
        App.get_running_app()._attemptLogin(
            username=username,
            password=password)

        #Unset the focus to hide the keyboard.
        self.ids.UsernameInput.focus = False
        self.ids.PasswordInput.focus = False

#======================================================
#   Other Stuff
#======================================================

#Just a placeholder that spawns other screens.
class TestScreen(Screen):
    def onButtonPress(self):
        App.get_running_app().addAndNavToScreen( TestScreen() )

#@TAG: I'm not sure why I have to do this, but I am not able to generate a popup
#through the .kv file.
class PopupMessage(Popup):

    title = StringProperty()
    message = StringProperty()

    def __init__(self, **kwargs):
        super(PopupMessage, self).__init__(**kwargs)
        self.title = kwargs['title']
        self.message = kwargs['message']

#======================================================
#   Main App
#======================================================

#First Widget of the app.  The layout contains top bar and main... visually area.
class Root(StackLayout):
    pass

#Base app.  Intended to be inherited from.
class Skeleton(App):

    #@TAG: Here is where I removed the sap service url.
    service_url = StringProperty('')
    sap_service = ObjectProperty(KivySapService())
    nav_stack = ListProperty([])
    nav_previous_enabled = BooleanProperty(False)

    app_name = StringProperty("App Name")

    def __init__(self, **kwargs):
        super(Skeleton, self).__init__(**kwargs)
        #TODO: If testing, replace sap_service with a fake service.

    def build(self):
        return Root()

    #Add a screen to the app's screen manager.
    def addScreen(self, screen):
        self.root.ids.MainWindow.add_widget(screen)

    #Set the screenmanager's active screen, including fancy transitions.
    def navToScreen(self, screen_name):
        self.root.ids.MainWindow.transition.direction = 'left'

        if self.root.ids.MainWindow.current != screen_name:
            self.nav_stack.append(screen_name)

        self.root.ids.MainWindow.current = screen_name

    #Add the screen to our app and navigate it.  Provide a unique screen name if
    #none is provided.
    def addAndNavToScreen(self, screen):
        # Add random screen name if none is present.
        if screen.name == '':
            screen.name = str(time.time())
            logging.info("Root Screen has no name, adding a random one.")

        self.addScreen(screen)
        self.navToScreen(screen.name)

        #Enable the back button if there's something to go back to.
        if(len(self.nav_stack) > 1):
            self.nav_previous_enabled = True

    #Navigate to the previous screen and remove the top screen's name from the
    #navstack.
    def navBack(self):
        if len(self.nav_stack) > 1:
            self.nav_stack.pop()
            self.root.ids.MainWindow.transition.direction = 'right'
            self.root.ids.MainWindow.current = self.nav_stack[-1]

            if len(self.nav_stack) <= 1:
                self.nav_previous_enabled = False

    #Show a popup message.
    def showMessage(self, title, message):
        popup = PopupMessage(title=title, message=message)
        popup.open()

    #Disable input for the entire app. Used when waiting on an asynchronous
    # data request.
    def disableInput(self):
        self.root.disabled = True

    #Alow input for the entire app.  Used when an asynchronous request returns.
    def enableInput(self):
        self.root.disabled = False

    #Called when the login button is pressed.
    def _attemptLogin(self, username, password):

        """
        self.sap_service.connect(
            url = self.service_url,
            username = username,
            password = password,
            on_success = self._onLogin,
            on_failure = self._onFailedLogin,
            blocking = False)

        self.disableInput()
        """
        #Bump-it.
        self._onLogin()

    #Called when a login is successful
    def _onLogin(self, *args):
        self.onLogin()
        self.enableInput()

    #Called when a login fails.
    def _onFailedLogin(self, *args):
        self.onFailedLogin()
        self.enableInput()


    #Intended to be overwritten.  Should utilize events for this probably.
    def onLogin(self):
        self.navToScreen("TestScreen")

    def onFailedLogin(self):
        self.showMessage("Login Error", "Error logging in.  Please check your credentials.")


if __name__ == '__main__':
    Skeleton().run()

