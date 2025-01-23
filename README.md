# Gym Dashboard - Your IOT Gym Management App

## How to use
There are 3 separate apps:
- app.py - web app
- sender.py - Raspberry Pi integration
- receiver.py - database integration

### Raspberry Pi
It has 2 use modes:
- register mode (red button, default mode)
- entry mode (green button)

You can check the current mode by looking at leds. If they are on, register mode is active.

After running sender.py, the oled screen will display a card image on a blue background. This means that it will read all cards placed on the reader. 

### Registering clients
To register a new client, go to the clients list and click Add Client button. After that, input your client's data. 

To add a card to the client, simply place the card on the reader when it is in register mode. If the card can be added to the new client, the oled will display a checkmark on a green background. If the card is already owned by a client, X on a red background will be displayed.

Existing clients can also have their cards changed the same way, except that instead of creating a new client, click edit button on the right side of the client.

### Entry and exit
Once clients are registered, they can enter and leave the gym. First, make sure to enable entry mode. Once that's done, they can place the card on the reader. If their cards are active, the buzzer will play a 1 second sound and a checkmark will be displayed and they can enter or exit the gym. If the cards aren't active or are not registered, X will be displayed and the buzzer will play 2 short sounds.

All successful entries and exits are displayed in the dashboard. You can also display stats of a single user by clicking their profile in the clients list.

## Screenshots

### Dashboard
![dashboard](https://raw.githubusercontent.com/PiotrO15/Gym-Dashboard-IOT/refs/heads/main/screenshots/dashboard.png)

### Clients list
![clients-list](https://raw.githubusercontent.com/PiotrO15/Gym-Dashboard-IOT/refs/heads/main/screenshots/clients-list.png)

### Add/edit client
![add-client](https://raw.githubusercontent.com/PiotrO15/Gym-Dashboard-IOT/refs/heads/main/screenshots/add-client.png)

### Client stats
![client-logs](https://raw.githubusercontent.com/PiotrO15/Gym-Dashboard-IOT/refs/heads/main/screenshots/client-logs.png)




