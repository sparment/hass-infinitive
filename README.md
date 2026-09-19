# Infinitive Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)


**THIS README IS A WIP!  Please let me know if parts of these instructions no longer work.**

This integration exists to enable users of the Bryant/Carrier HVAC units that are incompatible with smart thermostats (e.g. Nest, Eco, etc) to work with Home Assistant. This integration is reliant on the Infinitive project for establishing the hardware integration required to then interface with Home Assistant. Once you're done with these instructions you should have a thermostat in HA that controls your Bryant/Carrier HVAC unit.

## Installation Steps:

1. Buy a Raspberry Pi.
2. Buy a RS-485 USB adapter 11 for the Raspberry Pi -
[Here's an example](https://www.amazon.com/gp/product/B076WVFXN8/) but any RS-485 FTDI adapter should do.
3. Buy some wire - Search for ```18/2 thermostat wire```.  It's cheap and solid core.  You need enough to reach from your HVAC unit system board to the location of your RS-485 adapter.
  *Note: Some users have seen communication reliability issues with stranded core wire so solid core is preferred.  Not sure why but this is what we've observed.*
4. Flash the latest version of ```Raspberry Pi OS Lite``` to your SD card - [Here's](https://www.raspberrypi.com/software/) an all-in-one installer for Raspberry Pi OS.
5. Setup your Raspberry Pi OS install to have a fixed/static IP on your network - [Here's](https://raspberrypi-guide.github.io/networking/set-up-static-ip-address) a quick tutorial on setting a static IP.
6. Once the Pi is on your network we need to install the required packages:
   - For git and wget run the following:
     ```
     apt install git wget
     ```
     <details>
     <summary>Commands with "sudo"</summary>

     ```
     sudo apt install git wget
     ```
     </details>
   - For Go we want to download the latest version and install it manually (not using apt).  You can find the latest Go package on the [Go Website](https://go.dev/dl/).  If the latest version is newer please adjust the wget download link below.  For official Go installation instructions see [here](https://go.dev/doc/install).

     *Note: Latest version as of this writing is 1.19. Debian repos currently have 1.11 and that version does not work for what we need.*
     ```
     wget https://go.dev/dl/go1.19.linux-amd64.tar.gz
     rm -rf /usr/local/go && tar -C /usr/local -xzf go1.19.linux-amd64.tar.gz
     export PATH=$PATH:/usr/local/go/bin
     go install github.com/mww012/infinitive@latest
     ```
      <details>
      <summary>Commands with "sudo"</summary>

      ```
      wget https://go.dev/dl/go1.19.linux-amd64.tar.gz
      sudo rm -rf /usr/local/go && sudo tar -C /usr/local -xzf go1.19.linux-amd64.tar.gz
      sudo export PATH=$PATH:/usr/local/go/bin
      sudo go install github.com/mww012/infinitive@latest
      ```
      </details>

    <br>
7. Place this file at /etc/systemd/system/infinitive.service:

    Please update the ExecStart line to reflect your Go binary install location.  Mine was ```/root/go/bin/infintive``` but yours may be different.

    ```
    [Unit]
    Description=Infinitive Service
    After=network.target
    StartLimitIntervalSec=0
    [Service]
    Type=simple
    Restart=always
    RestartSec=1
    User=root
    ExecStart=/root/go/bin/infinitive -httpport=8080 -serial=/dev/ttyUSB0
    [Install]
    WantedBy=multi-user.target
    ```
    *Note:  If your RS-485 adapter does not show up as /dev/ttyUSB0 please adjust the file to reflect the proper device name.*
8. After the infinitive.service file has been created run the following:
    ```
    systemctl daemon-reload
    systemctl enable infinitive.service
    systemctl start infinitive.service
    ```
    <details>
    <summary>Commands with "sudo"</summary>

    ```
    sudo systemctl daemon-reload
    sudo systemctl enable infinitive.service
    sudo systemctl start infinitive.service
    ```
    </details>
9.  Run ```systemctl status infinitive``` to ensure that the service is running.
10. If all went well you should be able to browse to **http://[rasbperry_pi_IP]:8080** and be presented with the Infinitive web interface.  It won't have data until we connect everything up so let's do that.
11. Using the thermostat wire, connect one end to the RS-485 adapter as shown below:

    *Note: Don't connect to ports C and D on the HVAC system board.  Those are for power, not data, and you'll end up frying your RS-485 adapter.*

    - T/R+ (Green wire) connects to the A port on the HVAC system board.
    - T/R- (Yellow wire) connects to the B port on the HVAC system board.
    <details>
    <summary>Installation Pictures</summary>

    ![Pi RS-485 adapter connection](https://raw.githubusercontent.com/mww012/mww012.github.io/master/32cd71b515e2ae1436048976d6f6e33c6790abd7.jpeg)
    ![RS-485 adapter detail](https://raw.githubusercontent.com/mww012/mww012.github.io/master/708F50C1-0CBF-4CE7-87A8-468409863C49.jpeg)
    ![Carrier/Bryant system board](https://raw.githubusercontent.com/mww012/mww012.github.io/master/E11C5752-1FD6-4E68-A898-A77C1B9C6B9B.jpeg)
    </details>

    *At this point you should have data in your Infinitive web interface mentioned in the previous step.*

1.  Install the HA Infinitive integration
    <details>
    <summary>HACS Installation (Recommended)</summary>

    1. Install HACS in HA.  [Here](https://hacs.xyz/docs/setup/download) are instructions if you need them.
    2. Add ```https://github.com/sparment/hass-infinitive``` as a custom repository.  See [here](https://hacs.xyz/docs/faq/custom_repositories) for instructions.
    </details>
    <details>
    <summary>Manual Installation</summary>

    1. Download the [hass-infinitive repository](https://github.com/sparment/hass-infinitive)
    2. Copy the ```custom_components/infinitive``` folder into your HA custom_components folder.
    </details>

2.   Add this to your configuration.yaml:
     ```
     climate:
       - platform: infinitive
       host: [Raspberry Pi IP]
       port: 8080
     ```

3.  Restart Home Assistant

<br>

## If all worked properly you should see a climate.infinitive entity in HA now.  Good job following these crazy instructions!



