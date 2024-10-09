userSource = 'ESN_Users'

################ Companies

def addNewCompany(companyName,mqtt_topic,username,password,acls):
	#creates a new company in the system
	#   - new record in company table
	#   - new role in ESN User source

	query = "INSERT INTO company (company_name,mqtt_topic,created_on) VALUES (?,?,now())"
	params = [companyName,mqtt_topic]
	system.db.runPrepUpdate(query, params, "Administration")
	
	#create the role for this company
	system.user.addRole(userSource,mqtt_topic)
	
	# create the MQTT distributor user settings
	userProps = {"Username":username,"Password":password,"ACLs":acls}
	system.cirruslink.distributor.createConfig("Users", userProps)
	
	system.db.runPrepUpdate("create database ?", [companyName], "Administration")	
	system.db.addDatasource(jdbcDriver="PostgreSQL", name=companyName, description="Database for customer %s" % companyName, connectUrl="jdbc:postgresql://ice-postgresql.cluster-cpewoe8ks5ba.us-east-2.rds.amazonaws.com:5432/%s" % companyName.lower(), username="ignition", password="ice2bmoresec!", props="")
	
def deleteCompany(companyid,mqtt_topic):
	companyName = system.db.runScalarPrepQuery("SELECT company_name FROM company WHERE companyid=?", [companyid], "Administration")
	
	query = "DELETE FROM company WHERE mqtt_topic = ?"
	params = [mqtt_topic]
	system.db.runPrepUpdate(query, params, "Administration")
	
	# Removes the role from the ESN usersource.
	system.user.removeRole(userSource,mqtt_topic)
	
	# Removes the MQTT Distributor User
	usrs = system.cirruslink.distributor.readConfig("Users")
	for u in usrs:
		if u['Username'] == mqtt_topic:
			system.cirruslink.distributor.deleteConfig("Users", u['Id'])
			
	system.db.removeDatasource(companyName)

def changeCompanyDisplayName(companyid,newName):
	query = "UPDATE company set company_name = ? WHERE mqtt_topic = ?"
	params = [newName,companyid]
	system.db.runPrepUpdate(query, params, "Administration")

	return True


def updateCompanyMQTTSettings(companyid,newSettings,changePassword):
	usrs = system.cirruslink.distributor.readConfig("Users")
	for u in usrs:
		if u['Username'] == companyid:
			if changePassword:
				newSettings['Password'] = u['Password']
			#newSettings['Id'] = u['Id']
			logger = system.util.getLogger("myLogger")
		
			logger.info(str(newSettings))

			system.cirruslink.distributor.updateConfig("Users",u['Id'],"MergeOverwrite",newSettings)


################ Company Users
	

def addNewCompanyUser(companyName,email,initialPassword):
	#creates a new user for a company
	
	user = system.user.getUser(userSource, email)
	if user == None:
	
		# Get new user
		userToGet = system.user.getNewUser(userSource, email)
		  
		# Add user details
		contactInfo = {"email":email}
		userToGet.addContactInfo(contactInfo)
		userToGet.set("password", initialPassword)
		userToGet.addRoles([companyName])
		 
		# Adds a user to the the ESN usersource.
		system.user.addUser(userSource, userToGet)
	
	else:
		#Add Role to existing user if role does not already exists for the user
		if companyName not in user.roles:
			user.addRoles([companyName])
			system.user.editUser(userSource, user)

def removeCompanyUser(companyid,email):
	user = system.user.getUser(userSource, email)
	user.removeRole(companyid)
	system.user.editUser(userSource, user)

def updateCompanyUser(companyid,userid,email):
	pass

def createInitialPassword():
	import os, random, string
	
	length = 10
	chars = string.ascii_letters + string.digits + '!#$%'
	random.seed = (os.urandom(1024))
	
	password = ''.join(random.choice(chars) for i in range(length))


	return password
	
def resetUserPassword(email):

	from com.inductiveautomation.ignition.common.util import SecurityUtils
	
	newPassword = ESN.createInitialPassword()
	
	SHA1 = SecurityUtils.sha1String(newPassword)
	query = "UPDATE ign_users SET passwd=? WHERE username=?"
	system.db.runPrepUpdate(query, [SHA1, email],'Administration')

	return newPassword
