import parse

def doTest():
	damage_data = parse.getData()
	print("#### DAMAGE TEST ####")
	if damage_data["jigglypuff"]["Jab1"] == 3.0:
		print("jiggylypuff Jab1 -- PASS")
	else:
		print("jiggylypuff Jab1 -- FAIL")


	if damage_data["robin"]["U-smash"] == 15.0:
		print("robin U-smash -- PASS")
	else:
		print("robin U-smash -- FAIL")


	if damage_data["pikachu"]["Nair"] == 8.5: 
		print("pikachu Nair -- PASS")
	else:
		print("pikachu Nair -- FAIL")


	if damage_data["marth"]["Final Smash"] == 60.0: 
		print("marth Final Smash -- PASS")
	else:
		print("marth Final Smash -- FAIL")


	if damage_data["metaknight"]["U-throw"] == 10.0: 
		print("metaknight U-throw -- PASS")
	else:
		print("metaknight U-throw -- FAIL")


	if damage_data["falco"]["Reflector (ground)"] == 5.0: 
		print("falco Reflector (ground) -- PASS")
	else:
		print("falco Reflector (ground) -- FAIL")


	if damage_data["villager"]["Timber (axe)"] == 14.0: 
		print("village Timber (axe) -- PASS")
	else:
		print("village Timber (axe) -- FAIL")


	if damage_data["gamewatch"]["F-smash (normal)"] == 18.0: 
		print("gamewatch F-smash (normal) -- PASS")
	else:
		print("gamewatch F-smash (normal) -- FAIL")


	if damage_data["wiifit"]["Header (head spike)"] == 15.0: 
		print("wiifit Header (head spike) -- PASS")
	else:
		print("wiifit Header (head spike) -- FAIL")


	if damage_data["zelda"]["Phantom Strike (fully charged uppercut slash)"] == 12.0: 
		print("zelda Phantom Strike (fully charged uppercut slash) -- PASS")
	else:
		print("zelda Phantom Strike (fully charged uppercut slash) -- FAIL")
	print("#### DAMAGE TEST END  ####")

doTest()
