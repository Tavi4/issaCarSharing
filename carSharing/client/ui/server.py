import socket
import threading
import json

users = {
    "admin": {"password": "1234", "id": "001"},
    "user1": {"password": "abcd", "id": "002"},
    "test": {"password": "test", "id": "003"},
}

cars = {
    "1HGCM82633A123456": {"location": "Palas", "available": True, "lights": False, "doors_locked": True, "client_id": None},
    "1FAHP2E85BG120500": {"location": "Podu Ros", "available": True, "lights": False, "doors_locked": True, "client_id": None},
    "JH4KA9650MC123789": {"location": "Mall", "available": False, "lights": False, "doors_locked": True, "client_id": None},
}


def handle_client(client_socket):
    try:
        request = json.loads(client_socket.recv(1024).decode())
        print(f"Debug: Request received: {request}")
        action = request.get("action")
        print(f"Debug: Action received: {action}")

        # ------------- Login -------------
        if action == "login":
            username = request.get("username")
            password = request.get("password")
            user = users.get(username)
            if user and user["password"] == password:
                response = {"status": "success", "message": "Login successful", "id": user["id"]}
                print(f"Debug: Login succesful")
            else:
                response = {"status": "error", "message": "Invalid username or password"}

        # ------------- Query cars -------------
        elif action == "query_cars":
            available_cars = {vin: car for vin, car in cars.items() if car["available"]}
            response = {"status": "success", "cars": available_cars}

        # ------------- Start rental -------------
        elif action == "start_rental":
            vin = request.get("vin")
            client_id = request.get("client_id")

            print("----- start rental -----")
            print(f"VIN-ul primit: {vin}")
            print(f"Client id primit: {client_id}")

            if cars.get(vin) and cars[vin]["available"]:
                cars[vin]["available"] = False
                cars[vin]["client_id"] = users[client_id]["id"] # asociem clientul cu masina
                response = {"status": "success", "message": f"Car {vin} rental started!"}
            else:
                response = {"status": "error", "message": "Car not available or invalid VIN"}


        # ------------- End rental -------------
        elif action == "end_rental":
            vin = request.get("vin")
            client_id = request.get("client_id")
            if cars.get(vin) and not cars[vin]["available"]:
                if cars[vin]["doors_locked"] and not cars[vin]["lights"]:
                    cars[vin]["available"] = True
                    cars[vin]["client_id"] = None
                    response = {"status": "success", "message": f"Car {vin} rental ended!"}
                else:
                    response = {"status": "error", "message": "Ensure doors are locked and lights are off before ending rental."}
            else:
                response = {"status": "error", "message": "Car not rented or invalid VIN"}


        # ------------- Check car state -------------
        elif action == "check_car_state":
            vin = request.get("vin")
            if cars.get(vin):
                car = cars[vin]
                response = {
                    "status": "success",
                    "doors_locked": car["doors_locked"],
                    "lights_off": car["lights_off"],
                }
            else:
                response = {"status": "error", "message": "Invalid VIN"}


        # ------------- Validate client ID -------------
        elif action == "validate_client_id":
            vin = request.get("vin")
            client_id = request.get("client_id")

            print(f"VIN-ul primit: {vin}")
            print(f"Client id primit: {client_id}")
            vinn = cars[vin]["client_id"]
            print(f"cars[vin] client id: {vinn}")
            if not vin or not client_id:
                response = {"status": "error", "message": "VIN or Client ID missing"}
            elif vin in cars and cars[vin]["client_id"] == client_id:
                car = cars[vin]
                response = {
                    "status": "success",
                    "message": "Client ID is valid",
                    "doors_locked": car["doors_locked"],
                    "lights": car["lights"],
                }
            else:
                response = {"status": "error", "message": "Invalid VIN or Client ID"}


        elif action == "telematics_control":
            vin = request.get("vin")
            client_id = request.get("client_id")
            control = request.get("control")  # "unlock_doors", "lock_doors", "turn_on_lights", "turn_off_lights"

            if vin in cars:
                if cars[vin]["client_id"] == client_id:  # Verificăm dacă ID-ul clientului este valid
                    if control == "unlock_doors":
                        cars[vin]["doors_locked"] = False
                        response = {
                            "status": "success",
                            "message": "Doors unlocked.",
                            "lights": cars[vin]["lights"],
                            "doors_locked": cars[vin]["doors_locked"]
                        }
                    elif control == "lock_doors":
                        cars[vin]["doors_locked"] = True
                        response = {
                            "status": "success",
                            "message": "Doors locked.",
                            "lights": cars[vin]["lights"],
                            "doors_locked": cars[vin]["doors_locked"]
                        }
                    elif control == "turn_on_lights":
                        cars[vin]["lights"] = True
                        response = {
                            "status": "success",
                            "message": "Lights turned on.",
                            "lights": cars[vin]["lights"],
                            "doors_locked": cars[vin]["doors_locked"]
                        }
                    elif control == "turn_off_lights":
                        cars[vin]["lights"] = False
                        response = {
                            "status": "success",
                            "message": "Lights turned off.",
                            "lights": cars[vin]["lights"],
                            "doors_locked": cars[vin]["doors_locked"]
                        }
                    else:
                        response = {"status": "error", "message": "Invalid control command."}
                else:
                    response = {"status": "error", "message": "Invalid client ID for this car."}
            else:
                response = {"status": "error", "message": "Invalid VIN."}

        else:
            response = {"status": "error", "message": "Unknown action"}

        client_socket.send(json.dumps(response).encode())
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()



def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("127.0.0.1", 12345))
    server.listen(5)
    print("Server started on port 12345")

    while True:
        client_socket, _ = server.accept()
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()


if __name__ == "__main__":
    start_server()
