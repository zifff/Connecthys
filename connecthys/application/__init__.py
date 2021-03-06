#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------
# Application :    Connecthys, le portail internet de Noethys
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-16 Ivan LUCAS
# Licence:         Licence GNU GPL
#--------------------------------------------------------------


import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_adminlte import AdminLTE

import os.path
REP_APPLICATION = os.path.abspath(os.path.dirname(__file__))
REP_CONNECTHYS = os.path.dirname(REP_APPLICATION)


# Récupération du numéro de version de l'application
import updater
__version__ = updater.GetVersionActuelle()

print "version %s" % (__version__) 

# Init application
app = Flask(__name__)

# Configuration de flask
try :
    print "configuration 1 "
    from data.config import Config_application
    print "configuration 2 "
    app.config.from_object(Config_application)
    print "configuration 3 "
    app.config["VERSION_APPLICATION"] = __version__
    print "configuration 4 "
    config_ok = True
    print "configuration OK "
except :
    print "configuration KO "
    config_ok = False
	
    
# Flask compress
#from flask_compress import Compress
#compress = Compress()
#compress.init_app(app)

# Connexion avec le journal d'évènements
handler = RotatingFileHandler(os.path.join(REP_CONNECTHYS, "journal.log"), maxBytes=100000, backupCount=10)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('[%(asctime)s][%(levelname)s][%(filename)s:%(lineno)d] %(message)s')
handler.setFormatter(formatter)
app.logger.addHandler(handler)

# Connexion avec le journal de debug
handlerdebug = RotatingFileHandler(os.path.join(REP_CONNECTHYS, "debug.log"), maxBytes=204800, backupCount=30)
handlerdebug.setLevel(logging.DEBUG)
formatterdebug = logging.Formatter('[%(asctime)s][%(levelname)s][%(filename)s:%(lineno)d] %(message)s')
handlerdebug.setFormatter(formatterdebug)
app.logger.addHandler(handlerdebug)

app.logger.setLevel(logging.DEBUG)

if config_ok == True :

    # Debugtoolbar
    if Config_application.DEBUG == True :
        app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
        app.config['DEBUG_TB_PROFILER_ENABLED'] = True
        from flask_debugtoolbar import DebugToolbarExtension
        toolbar = DebugToolbarExtension(app)

    # Connexion avec flask_login
    from flask_login import LoginManager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    # Connexion avec SqlAlchemy
    from flask_sqlalchemy import SQLAlchemy
    db = SQLAlchemy(app)

    # Connexion avec flask_migrate
    from flask_script import Manager
    from flask_migrate import Migrate, MigrateCommand
    migrate = Migrate(app, db)
    manager = Manager(app)
    manager.add_command('db', MigrateCommand)

    # Connexion avec AdminLTE
    AdminLTE(app)

    # Flask-WTF csrf protection
    from flask_wtf.csrf import CSRFProtect 
    csrf = CSRFProtect()  
    csrf.init_app(app)

    # Import des views et des models
    import models, views, utils

    # Recherche la version de la base de données
    versionDB = models.GetVersionDB()

    # Création de la base de données si nécessaire
    if versionDB == None :
        models.CreationDB()

    # Vérifie que la DB est à jour
    if versionDB != None :
        if updater.GetVersionTuple(__version__) > updater.GetVersionTuple(versionDB) :
            models.UpgradeDB()

# Si configuration absente     
if config_ok == False :
    AdminLTE(app)
    print "debug noconfig.html"
    print "Le portail est correctement installé mais n'a pas encore été synchronisé par l'administrateur."
    import noconfig
    
    