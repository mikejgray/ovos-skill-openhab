# -*- coding: iso-8859-15 -*-
# pylint: disable=missing-function-docstring,missing-module-docstring,missing-class-docstring
#
# Copyright (c) 2010-2019 Contributors to the openHAB project
#
# See the NOTICE file(s) distributed with this work for additional
# information.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License 2.0 which is available at
# http://www.eclipse.org/legal/epl-2.0
#
# SPDX-License-Identifier: EPL-2.0
#
from ovos_workshop.intents import IntentBuilder
from ovos_workshop.skills import OVOSSkill
from rapidfuzz import fuzz

import requests

# v 0.1 - just switch on and switch off a fix light
# v 0.2 - code review
# v 0.3 - first working version on fixed light item
# v 0.4 - getTaggedItems method in order to get all the tagged items from openHAB
# v 0.5 - refresh tagged item intent
# v 0.6 - add findItemName method and import fuzzywuzzy
# v 0.7 - add intent for switchable items
# v 0.8 - merged lighting and switchable intent in onoff intent
# v 0.9 - added support to dimmable items
# v 1.0 - added Thermostat tag support
# v 1.1 - added what status Switchable tag
# v 1.2 - support to python 3.0
# v 1.3 - support german
# v 1.4 - support spanish
# v 1.5 - support to 19


__author__ = 'mortommy'

class openHABSkill(OVOSSkill):

    def __init__(self, *args, bus=None, skill_id='', **kwargs):
        super().__init__(*args, bus=bus, skill_id=skill_id, **kwargs)

        self.command_headers = {"Content-type": "text/plain"}
        self.polling_headers = {"Accept": "application/json"}

        self.lightingItemsDic = dict()
        self.switchableItemsDic = dict()
        self.currentTempItemsDic = dict()
        self.currentHumItemsDic = dict()
        #self.currentThermostatItemsDic = dict()
        self.targetTemperatureItemsDic = dict()
        #self.homekitHeatingCoolingModeDic = dict()
        self.getTaggedItems()

    def initialize(self):

        refresh_tagged_items_intent = IntentBuilder("RefreshTaggedItemsIntent").require("RefreshTaggedItemsKeyword").build()
        self.register_intent(refresh_tagged_items_intent, self.handle_refresh_tagged_items_intent)

        onoff_status_intent = IntentBuilder("OnOff_StatusIntent").require("OnOffStatusKeyword").require("Command").require("Item").build()
        self.register_intent(onoff_status_intent, self.handle_onoff_status_intent)

        dimmer_status_intent = IntentBuilder("Dimmer_StatusIntent").require("DimmerStatusKeyword").require("Item").optionally("BrightPercentage").build()
        self.register_intent(dimmer_status_intent, self.handle_dimmer_status_intent)

        #what_status_intent = IntentBuilder("What_StatusIntent").require("WhatStatusKeyword").require("Item").require("RequestType").build()
        #self.register_intent(what_status_intent, self.handle_what_status_intent)
        self.register_entity_file('item.entity')
        self.register_entity_file('requesttype.entity')
        self.register_intent_file('what.status.intent',self.handle_what_status_intent)

        setTemp_status_intent = IntentBuilder("SetTemp_StatusIntent").require("ThermostatStatusKeyword").require("Item").require("TempValue").build()
        self.register_intent(setTemp_status_intent, self.handle_setTemp_status_intent)

        list_items_intent = IntentBuilder("ListItemsIntent").require("ListItemsKeyword").build()
        self.register_intent(list_items_intent, self.handle_list_items_intent)

    def get_config(self, key):
        return (self.settings.get(key) or self.config_core.get('openHABSkill', {}).get(key))

    @property
    def host(self):
        return self.get_config('host')

    @property
    def port(self):
        return self.get_config('port')

    @property
    def url(self):
        if self.host and self.port:
            return f"http://{self.host}:{self.port}/rest"

    def getTaggedItems(self):
        #find all the items tagged Lighting and Switchable from openHAB
        #the labeled items are stored in dictionaries

        self.lightingItemsDic = {}
        self.switchableItemsDic = {}
        self.currentTempItemsDic = {}
        self.currentHumItemsDic = {}
        self.currentThermostatItemsDic = {}
        self.targetTemperatureItemsDic = {}
        self.homekitHeatingCoolingModeDic = {}

        if self.url is None:
            self.log.error("Configuration needed!")
            self.speak_dialog('ConfigurationNeeded')
        else:
            requestUrl = self.url+"/items?recursive=false"

            try: 
                req = requests.get(requestUrl, headers=self.polling_headers, timeout=5)
                if req.status_code == 200:
                    json_response = req.json()
                    for x in range(0,len(json_response)):
                        if ("Lighting" in json_response[x]['tags']):
                            self.lightingItemsDic.update({json_response[x]['name']: json_response[x]['label']})
                        elif ("Switch" in json_response[x]['tags'] or "Switchable" in json_response[x]['tags']):
                            self.switchableItemsDic.update({json_response[x]['name']: json_response[x]['label']})
                        elif ("CurrentTemperature" in json_response[x]['tags']):
                            self.currentTempItemsDic.update({json_response[x]['name']: json_response[x]['label']})
                        elif ("CurrentHumidity" in json_response[x]['tags']):
                            self.currentHumItemsDic.update({json_response[x]['name']: json_response[x]['label']})
                        elif ("Thermostat" in json_response[x]['tags']):
                            self.currentThermostatItemsDic.update({json_response[x]['name']: json_response[x]['label']})
                        elif ("TargetTemperature" in json_response[x]['tags']):
                            self.targetTemperatureItemsDic.update({json_response[x]['name']: json_response[x]['label']})
                        elif ("homekit:HeatingCoolingMode" in json_response[x]['tags']):
                            self.homekitHeatingCoolingModeDic.update({json_response[x]['name']: json_response[x]['label']})
                        else:
                            pass
                else:
                    self.log.error("Some issues with the command execution!")
                    self.log.error("Status code: %s" % (req.status_code))
                    self.log.error("OpenHAB response: %s" % (req.text))
                    self.speak_dialog('GetItemsListError')
                    return
            except KeyError:
                pass
            except Exception as err:
                self.log.error(f"Some issues with the command execution!\n{err}")
                self.speak_dialog('GetItemsListError')

    def findItemName(self, itemDictionary, messageItem):

        bestScore = 0
        score = 0
        bestItem = None

        try:
            for itemName, itemLabel in list(itemDictionary.items()):
                score = fuzz.ratio(messageItem, itemLabel, score_cutoff=bestScore)
                if score > bestScore:
                    bestScore = score
                    bestItem = itemName
        except KeyError:
                    pass

        return bestItem


    def getItemsFromDict(self, typeStr, itemsDict):
        if len(itemsDict) == 0:
            return ""
        else:
            return "%s: %s" % (typeStr, ', '.join(list(itemsDict.values())))

    def handle_list_items_intent(self, message):
        msg = self.getItemsFromDict("Lights", self.lightingItemsDic) + "\n"
        msg = msg.strip() + ' ' + self.getItemsFromDict("Switches", self.switchableItemsDic) + "\n"
        msg = msg.strip() + ' ' + self.getItemsFromDict("Current Temperature", self.currentTempItemsDic) + "\n"
        msg = msg.strip() + ' ' + self.getItemsFromDict("Current Humidity", self.currentHumItemsDic) + "\n"
        msg = msg.strip() + ' ' + self.getItemsFromDict("Thermostat", self.currentThermostatItemsDic) + "\n"
        msg = msg.strip() + ' ' + self.getItemsFromDict("Target Temperature", self.targetTemperatureItemsDic) + "\n"
        msg = msg.strip() + ' ' + self.getItemsFromDict("Homekit Heating and Cooling", self.homekitHeatingCoolingModeDic)
        self.speak_dialog('FoundItems', {'items': msg.strip()})

    def handle_refresh_tagged_items_intent(self, message):
        #to refresh the openHAB items labeled list we use an intent, we can ask the assistant to make the refresh

        self.getTaggedItems()
        dictLenght = str(len(self.lightingItemsDic) + len(self.switchableItemsDic) + len(self.currentTempItemsDic) + len(self.currentHumItemsDic) + len(self.currentThermostatItemsDic) + len(self.targetTemperatureItemsDic) + len(self.homekitHeatingCoolingModeDic))
        self.speak_dialog('RefreshTaggedItems', {'number_item': dictLenght})

    def handle_onoff_status_intent(self, message):
        command = message.data.get('Command')
        messageItem = message.data.get('Item')

        #We have to find the item to update from our dictionaries
        self.lightingSwitchableItemsDic = dict()
        self.lightingSwitchableItemsDic.update(self.lightingItemsDic)
        self.lightingSwitchableItemsDic.update(self.switchableItemsDic)

        ohItem = self.findItemName(self.lightingSwitchableItemsDic, messageItem)

        if ohItem is not None:
            if (command != "on") and (command != "off"):
                self.speak_dialog('ErrorDialog')
            else:
                statusCode = self.sendCommandToItem(ohItem, command.upper())
                if statusCode == 200:
                    self.speak_dialog('StatusOnOff', {'command': command, 'item': messageItem})
                elif statusCode == 404:
                    self.log.error("Some issues with the command execution!. Item not found")
                    self.speak_dialog('ItemNotFoundError')
                else:
                    self.log.error("Some issues with the command execution!")
                    self.speak_dialog('CommunicationError')
        else:
            self.log.error("Item not found!")
            self.speak_dialog('ItemNotFoundError')

    def handle_dimmer_status_intent(self, message):
        command = message.data.get('DimmerStatusKeyword')
        messageItem = message.data.get('Item')
        brightValue = message.data.get('BrightPercentage', None)

        statusCode = 0
        newBrightValue = 0

        ohItem = self.findItemName(self.lightingItemsDic, messageItem)

        if ohItem is not None:
            #if ((command == "set") or (command == "imposta") or (command == "setze") or (command == "pone")):
            if self.voc_match(command, 'Set'):
                if ((brightValue is None) or (int(brightValue) < 0) or (int(brightValue) > 100)):
                    self.speak_dialog('ErrorDialog')
                else:
                    statusCode = self.sendCommandToItem(ohItem, brightValue)
            else:
                #find current item statusCode
                state = self.getCurrentItemStatus(ohItem)
                if (state is not None):
                    #dim or brighten the value
                    curBrightList = state.split(',')
                    curBright = int(curBrightList[len(curBrightList)-1])

                    if(brightValue is None):
                        brightValue = "10"

                    #if ((command == "dim") or (command == "abbassa") or (command == "dimme") or (command == "oscurece")):
                    if self.voc_match(command, 'Dim'):
                        newBrightValue = curBright-(int(brightValue))
                    else:
                        newBrightValue = curBright+(int(brightValue))

                    if (newBrightValue < 0):
                        newBrightValue = 0
                    elif (newBrightValue > 100):
                        newBrightValue = 100
                    else:
                        pass

                    #send command to item
                    statusCode = self.sendCommandToItem(ohItem, str(newBrightValue))
                else:
                    pass

            if statusCode == 200:
                self.speak_dialog('StatusDimmer', {'item': messageItem})
            elif statusCode == 404:
                self.log.error("Some issues with the command execution!. Item not found")
                self.speak_dialog('ItemNotFoundError')
            else:
                self.log.error("Some issues with the command execution!")
                self.speak_dialog('CommunicationError')

        else:
            self.log.error("Item not found!")
            self.speak_dialog('ItemNotFoundError')

    def handle_what_status_intent(self, message):

        messageItem = message.data.get('item')
        self.log.debug("Item: %s" % (messageItem))
        requestType = message.data.get('requesttype')
        self.log.debug("Request Type: %s" % (requestType))

        unitOfMeasure = self.translate('Degree')
        infoType = self.translate('Temperature')

        self.currStatusItemsDic = dict()

        if self.voc_match(requestType, 'Temperature'):
            self.currStatusItemsDic.update(self.currentTempItemsDic)
        elif self.voc_match(requestType, 'Humidity'):
            unitOfMeasure = self.translate('Percentage')
            infoType = self.translate('Humidity')
            self.currStatusItemsDic.update(self.currentHumItemsDic)
        elif self.voc_match(requestType, 'Status'):
            infoType = self.translate('Status')
            unitOfMeasure = ""
            self.currStatusItemsDic.update(self.switchableItemsDic)
        else:
            self.currStatusItemsDic.update(self.targetTemperatureItemsDic)

        ohItem = self.findItemName(self.currStatusItemsDic, messageItem)

        if ohItem is not None:
            state = self.getCurrentItemStatus(ohItem)
            self.speak_dialog('TempHumStatus', {'item': messageItem, 'temp_hum': infoType, 'temp_hum_val': state, 'units_of_measurement': unitOfMeasure})
        else:
            self.log.error(f"Item {messageItem} not found!")
            self.speak_dialog('ItemNotFoundError')

    def handle_setTemp_status_intent(self, message):
        command = message.data.get('ThermostatStatusKeyword')
        messageItem = message.data.get('Item')
        tempVal = message.data.get('TempValue')

        statusCode = 0
        newTempValue = 0

        ohItem = self.findItemName(self.targetTemperatureItemsDic, messageItem)

        if ohItem is not None:
            if self.voc_match(command, 'Regulate'):
                statusCode = self.sendCommandToItem(ohItem, tempVal)
                newTempValue = tempVal
            else:
                state = self.getCurrentItemStatus(ohItem)
                if ((state is not None) and (state.isdigit())):
                    if self.voc_match(command, 'Increase'):
                        newTempValue = int(state)+(int(tempVal))
                    else:
                        newTempValue = int(state)-(int(tempVal))

                    statusCode = self.sendCommandToItem(ohItem, str(newTempValue))
                else:
                    pass

            if statusCode == 200:
                self.speak_dialog('ThermostatStatus', {'item': messageItem, 'temp_val': str(newTempValue)})
            elif statusCode == 404:
                self.log.error(f"Some issues with the command execution! Item {messageItem} not found")
                self.speak_dialog('ItemNotFoundError')
            else:
                self.log.error("Some issues with the command execution!")
                self.speak_dialog('CommunicationError')

        else:
            self.log.error("Item not found!")
            self.speak_dialog('ItemNotFoundError')

    def sendStatusToItem(self, ohItem, command):
        requestUrl = self.url+"/items/%s/state" % (ohItem)
        req = requests.put(requestUrl, data=command, headers=self.command_headers, timeout=5)
        if req.status_code > 299:
            self.log.error("Unable to send status to item %s" % (ohItem))
            self.log.error(req.text)

        return req.status_code

    def sendCommandToItem(self, ohItem, command):
        requestUrl = self.url+"/items/%s" % (ohItem)
        req = requests.post(requestUrl, data=command, headers=self.command_headers, timeout=5)
        if req.status_code > 299:
            self.log.error("Unable to send command to item %s" % (ohItem))
            self.log.error(req.text)

        return req.status_code

    def getCurrentItemStatus(self, ohItem):
        requestUrl = self.url+"/items/%s/state" % (ohItem)
        state = None

        try:
            req = requests.get(requestUrl, headers=self.command_headers, timeout=5)

            if req.status_code == 200:
                state = req.text
            else:
                self.log.error("Some issues with the command execution!")
                self.log.error("Status code: %s" % (req.status_code))
                self.log.error("OpenHAB response: %s" % (req.text))
                self.speak_dialog('CommunicationError')

        except KeyError:
            pass

        return state

    def stop(self):
        pass
