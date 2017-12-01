# GameLogsToJson
Convert protobuf binary files to a convenient JSON format

Pour utiliser cet utilitaire :

- Cloner ce repository : https://github.com/google/protobuf
- Suivre ces instructions pour compiler protobuf : https://github.com/google/protobuf/blob/master/src/README.md
- Cloner ce repository : https://github.com/RoboCup-SSL/ssl-logtools
- Suivre ces instructions pour compiler ssl-logtools : https://github.com/RoboCup-SSL/ssl-logtools/blob/master/README.md
- Remplacer le fichier ssl-logtools/src/examples/examplereader.cpp par le examplereader.cpp présent dans ce repository
- Aller dans ssl-logtools/build/src/examples dans un terminal
- Exécuter la commande "make examplereader"
- L'exécutable se trouve dans ssl-logtools/build/bin/examplereader
- L'appel à l'utilitaire se fait comme ceci : "examplereader <log file>"
