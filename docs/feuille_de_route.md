# Fondamentaux

cf https://ricou.eu.org/pres_dem_perm.pdf

## Domaine 

Chaque domaine représente un sujet de gouvernance particulier auquel
est attaché un adjoint (élu). Voici les domaines prévus pour comencer :

* Culture,
* Sport,
* Environnement,
* Transports,
* Sécurité,
* Santé,
* Emploi,
* Éducation.
* Numérique (comprend le suivi de ce projet)

## Interface

Chaque électeur peut voir pour chaque électeur :

* le nombre de voix dont il dispose et sa progression
* le graphe des votes publics qui aboutissent à lui
* l'ensemble des personnes publiques qui reçoivent sa voix
* s’il accepte des voix ou pas
* sa description (page personnelle)
* ses interventions publiques dans les forums

De plus il a une vision globale qui lui permet de voir :

* la liste des élus
* le classement des électeurs par nombre de voix dans chaque domaine
* les électeurs qui correspondent à ses critères (moteur de recherche)

# Technique

## Architecture globale

L'authentification des utilisateurs est réalisée via un service tiers comme
Google. Voir un exemple d'implémentation dans le répertoire des sources.

Chaque service est implémenté comme une API RESTful.

## Serveur de vote

Python / Django REST Framework

## Serveur réseau social

Python / Django REST Framework


