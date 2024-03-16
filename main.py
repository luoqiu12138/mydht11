"""

MakeCode editor extension for DHT11 and DHT22 humidity/temperature sensors
by Alan Wang

"""
# % block="DHT11"
# % block="DHT22"
class DHTtype(Enum):
    DHT11 = 0
    DHT22 = 1
# % block="humidity"
# % block="temperature"
class dataType(Enum):
    humidity = 0
    temperature = 1
# % block="Celsius (*C)"
# % block="Fahrenheit (*F)"
class tempType(Enum):
    celsius = 0
    fahrenheit = 1
# % block="DHT11/DHT22" weight=100 color=#ff8f3f icon="\uf043"
@namespace
class dht11_dht22:
    _temperature: number = -999.0
    _humidity: number = -999.0
    _temptype: tempType = tempType.celsius
    _readSuccessful: bool = False
    _sensorresponding: bool = False
    """
    
    Query data from DHT11/DHT22 sensor. If you are using 4 pins/no PCB board versions, you'll need to pull up the data pin. 
    It is also recommended to wait 1 (DHT11) or 2 (DHT22) seconds between each query.
    
    """
    # % block="Query $DHT|Data pin $dataPin|Pin pull up $pullUp|Serial output $serialOtput|Wait 2 sec after query $wait"
    # % pullUp.defl=true
    # % serialOtput.defl=false
    # % wait.defl=true
    # % blockExternalInputs=true
    def queryData(DHT: DHTtype, dataPin: DigitalPin, pullUp: bool, serialOtput: bool, wait: bool):
        global _humidity, _temperature, _readSuccessful, _sensorresponding
        # initialize
        startTime: number = 0
        endTime: number = 0
        checksum: number = 0
        checksumTmp: number = 0
        dataArray: List[bool] = []
        resultArray: List[number] = []
        DHTstr: str = "DHT11" if (DHT == DHTtype.DHT11) else "DHT22"
        for index in range(40):
            dataArray.append(False)
        for index2 in range(5):
            resultArray.append(0)
        _humidity = -999.0
        _temperature = -999.0
        _readSuccessful = False
        _sensorresponding = False
        startTime = input.running_time_micros()
        # request data
        pins.digital_write_pin(dataPin, 0)
        # begin protocol, pull down pin
        basic.pause(18)
        if pullUp:
            pins.set_pull(dataPin, PinPullMode.PULL_UP)
        # pull up data pin if needed
        pins.digital_read_pin(dataPin)
        # pull up pin
        control.wait_micros(40)
        if pins.digital_read_pin(dataPin) == 1:
            if serialOtput:
                serial.write_line(DHTstr + " not responding!")
                serial.write_line("----------------------------------------")
        else:
            _sensorresponding = True
            while pins.digital_read_pin(dataPin) == 0:
                pass
            # sensor response
            while pins.digital_read_pin(dataPin) == 1:
                pass
            # sensor response
            # read data (5 bytes)
            for index3 in range(40):
                while pins.digital_read_pin(dataPin) == 1:
                    pass
                while pins.digital_read_pin(dataPin) == 0:
                    pass
                control.wait_micros(28)
                # if sensor still pull up data pin after 28 us it means 1, otherwise 0
                if pins.digital_read_pin(dataPin) == 1:
                    dataArray[index3] = True
            endTime = input.running_time_micros()
            # convert byte number array to integer
            for index4 in range(5):
                for index22 in range(8):
                    if dataArray[8 * index4 + index22]:
                        resultArray[index4] += 2 ** (7 - index22)
            # verify checksum
            checksumTmp = resultArray[0] + resultArray[1] + resultArray[2] + resultArray[3]
            checksum = resultArray[4]
            if checksumTmp >= 512:
                checksumTmp -= 512
            if checksumTmp >= 256:
                checksumTmp -= 256
            if checksum == checksumTmp:
                _readSuccessful = True
            # read data if checksum ok
            if _readSuccessful:
                if DHT == DHTtype.DHT11:
                    # DHT11
                    _humidity = resultArray[0] + resultArray[1] / 100
                    _temperature = resultArray[2] + resultArray[3] / 100
                else:
                    # DHT22
                    temp_sign: number = 1
                    if resultArray[2] >= 128:
                        resultArray[2] -= 128
                        temp_sign = -1
                    _humidity = (resultArray[0] * 256 + resultArray[1]) / 10
                    _temperature = (resultArray[2] * 256 + resultArray[3]) / 10 * temp_sign
                if _temptype == tempType.fahrenheit:
                    _temperature = _temperature * 9 / 5 + 32
            # serial output
            if serialOtput:
                serial.write_line(DHTstr + " query completed in " + str((endTime - startTime)) + " microseconds")
                if _readSuccessful:
                    serial.write_line("Checksum ok")
                    serial.write_line("Humidity: " + str(_humidity) + " %")
                    serial.write_line("Temperature: " + str(_temperature) + str((" *C" if _temptype == tempType.celsius else " *F")))
                else:
                    serial.write_line("Checksum error")
                serial.write_line("----------------------------------------")
        # wait 2 sec after query if needed
        if wait:
            basic.pause(2000)
    """
    
    Read humidity/temperature data from lastest query of DHT11/DHT22
    
    """
    # % block="Read $data"
    def readData(data: dataType):
        return _humidity if data == dataType.humidity else _temperature
    """
    
    Select temperature type (Celsius/Fahrenheit)"
    
    """
    # % block="Temperature type: $temp" advanced=true
    def selectTempType(temp: tempType):
        global _temptype
        _temptype = temp
    """
    
    Determind if last query is successful (checksum ok)
    
    """
    # % block="Last query successful?"
    def readDataSuccessful():
        return _readSuccessful
    """
    
    Determind if sensor responded successfully (not disconnected, etc) in last query
    
    """
    # % block="Last query sensor responding?" advanced=true
    def sensorrResponding():
        return _sensorresponding