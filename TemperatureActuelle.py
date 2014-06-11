# -*- coding:Latin-1 -*- # Permet d'utiliser les caractères français.

#Import des modules nécessaires
from xml.dom.minidom import parse
import urllib, string, arcpy, time


#Fonction pour ouvrir et lire le fichier XML.
def xmldescription(url):
    xmlfilename =urllib.urlopen(url) #Ouverture du fichier via le web.
    dom= parse(xmlfilename) #Lecture du fichier
    Description = dom.getElementsByTagName('summary') #Recherche l'élément 'summary'

    nbSummary = len(Description) #Nombre de summary
    condition = False
    NoSummary = 1
    while condition == False:
        if string.count(Description[NoSummary].firstChild.nodeValue ,u"Température:"):
            TxtNodeValue = Description[NoSummary].firstChild.nodeValue #Retourne le X ieme enfant du noeud soit le sommaire HTML
            condition = True
        NoSummary = NoSummary + 1
        if NoSummary == nbSummary:
            TxtNodeValue = "nil"
            condition = True

    # Traitement du noeud XML
    ListeB = string.split(TxtNodeValue, "<b>") # Division des informations du noeud à '<b>' retourne un liste de plusieurs éléments.

    if len(ListeB) > 1: # S'il y a de l'information dans la variable
            for elements in ListeB: # Pour chaque élément de la liste.
                if string.count(elements, "Temp") > 0: # S'il y a le texte 'TEMP' dans l'élément regardé.
                        TextTemp = string.split(elements, "</b>")[1] # Division pour extraire la température
                        NombreTemp = string.replace(TextTemp, "&deg;C <br/>", "") # Efface par remplacement les éléments indésirables
    else:
            NombreTemp = "-9999" # Si aucune température, mettre la valeur -9999.

    return string.strip(string.replace(NombreTemp, ",", ".")) # Retour de la valeur avec remplacement des , par des .

N = 0
while N < 23:

    fc = r"D:\Projets\MeteoPython\BD_Meteo.gdb\SationsMeteoQuebec" # Classe d'entités où se trouve l'information.
    fields = ('ville', 'url', 'Temperature') # Les champs à lire.

    with arcpy.da.UpdateCursor(fc, fields) as cursor: # Initialisation du curseur.
        for row in cursor:
            print row[0] + ":" + xmldescription("http://meteo.gc.ca/rss/city/" + row[1] ) # Concaténation de la donnée du champ url et le texte pour faire le lien url. De plus envoi des infos dans la fonction xmldescription().
            row[2] = float(xmldescription("http://meteo.gc.ca/rss/city/" + row[1]))
            cursor.updateRow(row) # Mise à jour du champ de température de la classe d'entités.

    if arcpy.CheckOutExtension("Spatial") =="CheckedOut": # Vérification si le module Spatial Analyst est activé.
        arcpy.env.workspace = r"D:\Projets\MeteoPython\BD_Meteo.gdb" # Définition de l'espace de travail pour les commandes suivantes.
        arcpy.MakeFeatureLayer_management(fc, "PointsMeteo_lyr", '"Temperature" > -9999') # Enlève les -9999 via une requête de définition pour l'interpolation.
        OutIMG = arcpy.sa.Idw("PointsMeteo_lyr", "Temperature","","","VARIABLE 8", "limits") # Interpolation IDW des valeurs de température.
        arcpy.env.overwriteOutput = 1 # Écrase le fichier s'il existe
        arcpy.Clip_management(OutIMG, "-8881010.42143521 5620161.08275039 -6356953.62302241 9003041.17894863", "IDWTemperature", "ProvinceQc","-3.402823e+038","ClippingGeometry","NO_MAINTAIN_EXTENT") # Clip selon la Province.

    mxd = arcpy.mapping.MapDocument(r"D:\Projets\MeteoPython\meteo.mxd") # Définition du mxd.
    #arcpy.mapping.ExportToPDF(mxd, "c:\\temp\\Meteo.pdf") # Export en PDF
    arcpy.mapping.ExportToJPEG(mxd, "C:\\Users\\mcouture\\Dropbox\\CarteMétéoPQ\\IMG" + str(N) + "_" + time.strftime('%H') + "h.jpg")
    arcpy.Delete_management(OutIMG) # Efface l'image de l'interpolation.
    arcpy.Delete_management("PointsMeteo_lyr") # Efface le fichier LYR

    print N
    time.sleep(3600)




