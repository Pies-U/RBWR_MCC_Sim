import tkinter as tk
from tkdial import Meter
from TkAnalogScale import AnalogScale
import time
import threading

# Setting the reactor steam outflow (in rbwr its dependant on reactor power)
total_steam_outflow = 1000 #max 2000kg/s min 0kg/s

# Setting satndard relative water levels in cm
reactor_water_level = 0 #max +500cm min -500cm
hotwell_water_level = 0 #max +500cm min -500cm
dearetor_water_level = 0 #max +50cm min -50cm
## need the levels value in kgs for simulating waterflow
reactor_water_amount = 100000 #kgs for the level of 0
hotwell_water_amount = 100000 #kgs for the level of 0
deareator_water_amount = 10000 #kgs for the level of 0 

# Setting starting values for pumps and valves
feedwater_pump1_enabled = True
feedwater_pump2_enabled = True

feedwater_pump1_valve = 1000 # Min 0 Max 1000 kg/s
feedwater_pump2_valve = 100 # Min 0 Max 1000 kg/s

condensate_pump1_enabled = True
condensate_pump2_enabled = True

condensate_pumps_valve = 1200 # Min 0 Max 2000 kg/s

# Game and main loop variable
keep_game_loop = True
keep_main_loop = True

#Time of time step
time_step_length = 1 #sec

def checkwaterlevels():
    global keep_game_loop
    if reactor_water_level < -500:
        keep_game_loop = False
        print("reactor level too low - terminating simulation")
    if reactor_water_level > 500:
        keep_game_loop = False
        print("reactor level too high - terminating simulation")

    if hotwell_water_level < -500:
        keep_game_loop = False
        print("hotwell level too low - terminating simulation")
    if hotwell_water_level > 500:
        keep_game_loop = False
        print("hotwell level too high - terminating simulation")
    
    if dearetor_water_level < -50:
        keep_game_loop = False
        print("reactor level too low - terminating simulation")
    if dearetor_water_level > 50:
        keep_game_loop = False
        print("dea level too high - terminating simulation")

def adjustvalve(valve: "feed_valve1, feed_valve2, cond_valve", adjustement_value: int):
    # function for standardised valve adjustements
    # allow write to global vars
    global feedwater_pump1_valve
    global feedwater_pump2_valve
    global condensate_pumps_valve

    # match for short valve names: feed_valve1, feed_valve2, cond_valve
    # make sure adjustement is possible
    # adjust or print error
    match valve:
        case "feed_valve1":
            if feedwater_pump1_valve + adjustement_value >= 1000:
                print("feed_valve1 value is max - cant adjust")
            elif feedwater_pump1_valve + adjustement_value <= 0:
                print("feed_valve1 value is min - cant adjust")
            else:
                feedwater_pump1_valve += adjustement_value
        case "feed_valve2":
            if feedwater_pump2_valve + adjustement_value >= 1000:
                print("feed_valve2 value is max - cant adjust")
            elif feedwater_pump2_valve + adjustement_value <= 0:
                print("feed_valve2 value is min - cant adjust")
            else:
                feedwater_pump2_valve += adjustement_value
        case "cond_valve":  
            if condensate_pumps_valve + adjustement_value >= 2000:
                print("cond_valve value is max - cant adjust")
            elif condensate_pumps_valve + adjustement_value <= 0:
                print("cond_valve value is min - cant adjust")
            else:
                condensate_pumps_valve += adjustement_value

def simulatewaterflow():
    #water exits the reactor as steam and condenses in the hotwell
    #water from the hotwell gets pumped to the deareator using condensate pumps and through condensate valve
    #water from the deareator gets pumped into the reactor vessel using feedwater pumps and through feedwater valves
    
    #total steam outflow -reactor_level +hotwell_level
    #condensate outflow -hotwell_level +deareator_level
    #feedwater flow -deareator_level +reactor_level
    
    #allow write of global vars
    global reactor_water_amount
    global hotwell_water_amount
    global deareator_water_amount

    # Calculate condenaste outflow
    condensate_outflow = 0
    if condensate_pump1_enabled and condensate_pump2_enabled:
        condensate_outflow = condensate_pumps_valve
    elif condensate_pump1_enabled ^ condensate_pump2_enabled:
        condensate_outflow = min(condensate_pumps_valve, 1000)
        
    # Calculate feedwater flow
    feedwater_flow = 0
    if feedwater_pump1_enabled:
        feedwater_flow += feedwater_pump1_valve
    if feedwater_pump2_enabled:
        feedwater_flow += feedwater_pump2_valve


    # Calculate flow deltas
    reactor_water_amount_delta = feedwater_flow - total_steam_outflow
    hotwell_water_amount_delta = total_steam_outflow - condensate_outflow
    deareator_water_amount_delta = condensate_outflow - feedwater_flow
    
    # Apply changes using deltas
    reactor_water_amount += reactor_water_amount_delta
    hotwell_water_amount += hotwell_water_amount_delta
    deareator_water_amount += deareator_water_amount_delta

    # Make vars as atributes
    simulatewaterflow.feedwater_flow = feedwater_flow
    simulatewaterflow.condensate_outflow = condensate_outflow
    simulatewaterflow.reactor_water_amount_delta = reactor_water_amount_delta
    simulatewaterflow.hotwell_water_amount_delta = hotwell_water_amount_delta
    simulatewaterflow.deareator_water_amount_delta = deareator_water_amount_delta

    if feedwater_pump1_enabled:
        simulatewaterflow.feedwater_flow1 = feedwater_pump1_valve
    if feedwater_pump2_enabled:
        simulatewaterflow.feedwater_flow2 = feedwater_pump2_valve
    
    time.sleep(time_step_length)

def printmccstatus():
    print(f"Reactor:  {reactor_water_amount}kg | {simulatewaterflow.reactor_water_amount_delta} {chr(916)}kg/s")
    print(f"Hotwell:   {hotwell_water_amount}kg | {simulatewaterflow.hotwell_water_amount_delta} {chr(916)}kg/s")
    print(f"Deareator: {deareator_water_amount}kg | {simulatewaterflow.deareator_water_amount_delta} {chr(916)}kg/s")
    print("=====================================")
    print(f"Total  steam  outflow: {total_steam_outflow}kg/s")
    print("-------------------------------------")
    print(f"Condensate pumps flow: {simulatewaterflow.condensate_outflow}kg/s")
    print("-------------------------------------")
    print(f"Total  feedwater flow: {simulatewaterflow.feedwater_flow}kg/s")
    print(f"Feedwater pump 1 flow: {simulatewaterflow.feedwater_flow1}kg/s")
    print(f"Feedwater pump 2 flow: {simulatewaterflow.feedwater_flow2}kg/s")
    print()

#Main loop
def game_func():
    while keep_game_loop:
        checkwaterlevels()
        simulatewaterflow()
        printmccstatus()
        #input("next step?")
    #    time.sleep(time_step_length)
    print("simulation was terminated")

## todo
#gui
#leaks

game_thread=threading.Thread(target=game_func, daemon=True)
game_thread.start()

root = tk.Tk()
root.title("RBWR_MCC_Simulator")
root.resizable(width=False, height=False)
root.geometry("1200x680")

#Sliders block
slidemeters = tk.Frame(root, height=230, width=1020, bg="red")
slidemeters.place(x=10,y=0)

totalsteamflowscale = AnalogScale(slidemeters, scale_text="Total Steam Flow", to=2000, bg="#dff0d9")
totalsteamflowscale.place(x=340, y=10)
totalsteamflowscale.set(total_steam_outflow)

totalfeedwaterflowscale = AnalogScale(slidemeters, scale_text="Total Feedwater Flow", to=2000, bg="#dff0d9")
totalfeedwaterflowscale.place(x=680, y=10)
totalfeedwaterflowscale.set(simulatewaterflow.feedwater_flow)

totalcondensateflowscale = AnalogScale(slidemeters, scale_text="Total Condensate Flow", to=2000, bg="#dff0d9")
totalcondensateflowscale.place(x=680, y=120)
totalcondensateflowscale.set(simulatewaterflow.condensate_outflow)

feedwaterflowscale1 = AnalogScale(slidemeters, scale_text="Feedwater Flow #1", to=1000, bg="#dff0d9")
feedwaterflowscale1.place(x=0, y=120)
feedwaterflowscale1.set(simulatewaterflow.feedwater_flow1)

feedwaterflowscale2 = AnalogScale(slidemeters, scale_text="Feedwater Flow #2", to=1000, bg="#dff0d9")
feedwaterflowscale2.place(x=340, y=120)
feedwaterflowscale2.set(simulatewaterflow.feedwater_flow2)


#Circular gauges block
valvemeters = tk.Frame(root, height=200, width=650, bg="red")
valvemeters.place(x=0, y=250)

feedwatervalvemeter1 = Meter(valvemeters, radius=200, start_angle=200, end_angle=-220, minor_divisions=2, text="", bg="#141414", fg="#dff0d9", axis_color="#141414", needle_color="#141414")
feedwatervalvemeter1.place(x=0, y=0)
feedwatervalvemeter1.set(feedwater_pump1_valve / 10)
feedwatervalvemeter2 = Meter(valvemeters, radius=200, start_angle=200, end_angle=-220, minor_divisions=2, text="", bg="#141414", fg="#dff0d9", axis_color="#141414", needle_color="#141414")
feedwatervalvemeter2.place(x=210, y=0)
feedwatervalvemeter2.set(feedwater_pump2_valve / 10)

condensatevalvemeter = Meter(valvemeters, radius=200, start_angle=200, end_angle=-220, minor_divisions=2, text="", bg="#141414", fg="#dff0d9", axis_color="#141414", needle_color="#141414")
condensatevalvemeter.place(x=450, y=0)
condensatevalvemeter.set(condensate_pumps_valve / 20)


root.mainloop()