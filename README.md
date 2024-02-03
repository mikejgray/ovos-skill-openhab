# <img src='https://www.openhab.org/openhab-logo-square.png' card_color='#40DBB0' width='50' height='50' style='vertical-align:bottom'/> openHAB
This skill adds openHAB support to OVOS/Neon.  **Please note that this is not an official OVOS or Neon skill. This version of the openHAB skill is not maintained by the openHAB community.**

## About 
This skill adds [openHAB](http://www.openhab.org/) support to [OVOS](https://openvoiceos.org).
The skill takes advantage of the openHAB REST API, so it works both with the v1.x and v2.x of openHAB.

In order to make openHAB Items accessible to OVOS/Neon, they need to be [tagged](https://www.openhab.org/addons/integrations/homekit/).
Device names recognized by OVOS/Neon are matched against openHAB Item Labels.

The above examples would all work with the following set of openHAB Item definitons:

```java
Color DiningroomLight "Diningroom Light" <light> (gKitchen) [ "Lighting" ] {channel="hue:0200:1:bloom1:color"}
Color KitchenLight "Kitchen Light" <light> (gKitchen) [ "Lighting" ] {channel="hue:0200:1:bloom1:color"}
Switch GoodNight "Good Night"	[ "Switchable" ]

Number MqttID1Temperature "Bedroom Temperature" <temperature> [ "CurrentTemperature" ] {mqtt="<[mosquitto:mysensors/SI/1/1/1/0/0:state:default]"}
Number MqttID1Humidity "Bedroom Humidity" [ "CurrentHumidity" ] {mqtt="<[mosquitto:mysensors/SI/1/0/1/0/1:state:default]"}

Group gThermostat "Main Thermostat" [ "gMainThermostat" ]
Number MainThermostatCurrentTemp "Main Thermostat Current Temperature" (gMainThermostat) [ "CurrentTemperature" ]
Number MainThermostatTargetTemperature "Main Thermostat Target Temperature" (gMainThermostat) [ "TargetTemperature" ]
String MainThermostatHeatingCoolingMode "Main Thermostat Heating/Cooling Mode" (gMainThermostat) [ "homekit:HeatingCoolingMode" ]
```

If items are modified in openHAB, a refresh in OVOS/Neon is needed by the command:

- *"Hey Mycroft/Neon, refresh openhab items"*

If you've forgotten what items have been identified, you can ask OVOS/Neon:
- *"Hey Mycroft/Neon, list openhab items"*

## Versions Change Log
* 2.0 refactor/modernization to support OVOS and Neon (provided AS-IS, no guarantee it works, I have no way of testing and the code hadn't been touched in 4 years. Here be dragons)
* 1.5 addedd support to core v19
* 1.4 added spanish translation
* 1.3 added german translation
* 1.2 addedd python 3 support
* 1.1 added status request to Switchable items
* 1.0 added support to item tagged as Thermostat, CurrentTemperature, CurrentHumidity
* 0.9 added dimming command to item tagged as Lighting
* 0.8 supports only Lighting and Switchable tags, commands ON and OFF

## Installation

In OVOS and Neon, skill installation occurs via pip. To install the openHAB skill, run the following command:

```bash
pip install git+https://github.com/mikejgray/ovos-skill-openhab
```

In Neon, skill installation must happen in `~/.config/neon/neon.yaml` to persist:

```yaml
skills:
  default_skills:
    - git+https://github.com/mikejgray/ovos-skill-openhab
```

If `skills.default_skills` doesn't exist, add it. If it does, you only need to add the last line.

If you're running Neon, please note you will also need to blacklist the Home Assistant skill as it shares some intents with this skill: 
 
```yaml
skills: 
  blacklisted_skills: 
    - neon_homeassistant_skill.mikejgray 
``` 

After installation, the skill needs to be configured. In Neon, the path is `~/.config/neon/skills/ovos-skill-openhab.mikejgray/settings.json`. In OVOS, it is `~/.config/mycroft/skills/ovos-skill-openhab.mikejgray/settings.json`:

```json
{
    "host": "192.168.1.42",
    "port": 8080
}
```

Replace the host IP and port with your openHAB server's IP and port. The default port is 8080.

## Examples 
* "Hey Mycroft/Neon, turn on Diningroom Light"
* "Hey Mycroft/Neon, switch off Kitchen Light"
* "Hey Mycroft/Neon, put on Good Night"
* "Hey Mycroft/Neon, what is Good Night status?"
* "Hey Mycroft/Neon, what is the status of Good Night?"
* "Hey Mycroft/Neon, set Diningroom to 50 percent"
* "Hey Mycroft/Neon, dim Kitchen"
* "Hey Mycroft/Neon, bright Kitchen"
* "Hey Mycroft/Neon, dim Kitchen by 20 percent"
* "Hey Mycroft/Neon, what's Bedroom temperature?"
* "Hey Mycroft/Neon, tell me the temperature of Bedroom"
* "Hey Mycroft/Neon, what's the Bedroom humidity?"
* "Hey Mycroft/Neon, I'd like to know the humidity of Bedroom"
* "Hey Mycroft/Neon, adjust Main Thermostat to 21 degrees"
* "Hey Mycroft/Neon, regulate Main Thermostat to 20 degrees"
* "Hey Mycroft/Neon, decrease Main Thermostat by 2 degrees"
* "Hey Mycroft/Neon, increase Main Thermostat by 1 degrees"
* "Hey Mycroft/Neon, what is Main Thermostat is regulated to?"
* "Hey Mycroft/Neon, how the Main Thermostat tuned to?"

## Credits 
- @mortommy
- @mikejgray (fork)

## Category
**IoT**

## Tags
#openHAB
#smarthome
#IoT
#Automation
#opensource
