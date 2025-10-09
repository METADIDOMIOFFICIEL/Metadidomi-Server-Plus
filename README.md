[![Sponsor Lygos](https://img.shields.io/badge/Sponsor-Lygos-blue?style=for-the-badge)](https://pay.lygosapp.com/$etsmeta)
<!-- HERO -->

# Metadidomi Server Plus – L’innovation locale au service de votre cloud

> Imaginez un serveur personnel, élégant et puissant, qui transforme votre ordinateur en une véritable forteresse numérique. Metadidomi Server Plus, c’est bien plus qu’une application : c’est votre espace privé, votre cloud, votre centre de contrôle, votre liberté retrouvée.

---

## 🚀 Pourquoi choisir Metadidomi Server Plus ?

* **Un cloud personnel, sécurisé et rapide**
  Fini les abonnements et les serveurs distants : stockez, partagez et gérez vos fichiers chez vous, en toute confidentialité. L’interface web moderne vous donne accès à vos documents où que vous soyez, avec une sécurité renforcée par authentification JWT.

* **Base de données intelligente**
  Manipulez vos données comme un pro : collections, documents, règles de sécurité… tout est pensé pour vous offrir la puissance du cloud, sans compromis sur la simplicité.

* **Transfert de fichiers ultra-simple**
  Uploadez, téléchargez, organisez vos fichiers sur le réseau local ou distant, grâce à un serveur NAS intégré. La rapidité et la fiabilité sont au rendez-vous.

* **Administration centralisée**
  Gérez vos APIs, surveillez vos serveurs, pilotez tout depuis une interface graphique Windows intuitive. Un clic suffit pour démarrer, arrêter ou superviser chaque service.

* **Gestion des utilisateurs et des accès**
  Créez des comptes, attribuez des droits, gardez le contrôle total sur qui accède à quoi. La sécurité est au cœur du projet.

* **Logs et supervision en temps réel**
  Gardez un œil sur tout ce qui se passe : chaque action, chaque transfert, chaque connexion est consignée pour une transparence totale.

---

## 🌐 Une expérience pensée pour vous

Metadidomi Server Plus s’adapte à vos besoins : Les interfaces web sont accessibles depuis n’importe quel appareil, et l’application Windows vous offre une prise en main immédiate.

---

## 🔒 Sécurité et sérénité

Votre cloud, vos règles. Authentification par clé, tokens JWT, CORS strict, et la possibilité d’ajouter un reverse proxy HTTPS pour une tranquillité absolue.

---

## ✨ Fonctionnalités clés (détail technique, la plupart sont disponible dans la version compléte)

### Authentification & sécurité

* Authentification JWT moderne (access + refresh tokens)
* Gestion des clés API et authentification par clé
* CORS strict configurable
* Intégration possible de reverse proxy (Nginx / Caddy) pour TLS

### Stockage & NAS

* Stockage local avec accès SMB / WebDAV
* Partages réseau chiffrés optionnels
* Uploads/downlloads optimisés (chunking, reprise)

### Base de données

* Collections et documents (modèle type NoSQL léger)
* Règles et rôles par collection
* Endpoints pour CRUD et recherche

### Administration

* Interface Windows pour contrôle des services
* Dashboard web pour métriques, logs et supervision
* Gestion des tâches planifiées et services

### Audits & logs

* Fichiers de logs horodatés
* Visualisation en temps réel

---

```powershell

# Les ports 8000/5000/5002/5003/5004/8001 doivent etre disponible dans le pare-feu
New-NetFirewallRule -DisplayName "Metadidomi HTTP" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow (Dans la version compléte)
```
## 🔧 Utilisation minimale

* **Demarrer toujours un serveur avant d'acceder à son IU, si la page ne s'affiche pas reactualiser plusieurs fois la page, il est possible que le deamarrage du serveur prenne un peu de temps.
* **Le bouton Main UI est considéré comme la page d'acceuil pour acceder à d'autres pags (Dans la version compléte).

---
## 🔧 AMELIORATION DANS LA NOUVELLE VERSION 1.1.0 (Version compléte)

* **La creation de compte utilisateur dans la section "utilisateur" a été déplacer et fonctionne déja.
* **La suppression des dossiers dans le "Cloud Storage" fonctionne, l'IU a été retravaillée avec un cota d'importation de fichiers à 15Go.
* ** Le HTTPS est prit en charge avec un gestionnaire de fichier HOSTS interatif intégrer, chaque modification regenére le certificat ce qui vous permet d'avoir des certificats toujours à jours.
* ** Un gestionnaire de Base de données est intégrer pour vous permettre de modifier les données manuellement si besoin.
* ** Un moteur de recherche AZ a éte ajouter. Et bien d'autres.

---
## 📦 API – Exemples rapides

### Auth (connexion)

```
POST /api/auth/login
Body: { "username": "alice", "password": "••••" }
Response: { "accessToken": "ey...", "refreshToken": "ey..." }
```

### CRUD Document

```
GET /api/collections/:name/documents
POST /api/collections/:name/documents
PUT /api/collections/:name/documents/:id
DELETE /api/collections/:name/documents/:id
```
## 🖼️ Ressources visuelles

| Image 1 | Image 2 | Image 3 | Image 4 |
|---------|---------|---------|---------|
| ![](/docs/Capturer.PNG) | ![](/docs/Capturer2.PNG) | ![](/docs/Capturer3.PNG) | ![](/docs/Capturer4.PNG) |

| Image 5 | Image 6 | Image 7 | Image 8 |
|---------|---------|---------|---------|
| ![](/docs/Capturer5.PNG) | ![](/docs/Capturer6.PNG) | ![](/docs/Capturer7.PNG) | ![](/docs/Capturer8.PNG) |


## ✉️ Contact

**Essayez Metadidomi Server Plus dès aujourd’hui et faites entrer le cloud chez vous.**
Contact : [infos.contact.metadidomi@gmail.com](mailto:infos.contact.metadidomi@gmail.com)

---

## 🧾 Licence & crédits

La version CORE est Distribué sous la licence MIT. La version compléte est proprietaire de ETS METADIDOMI sous licence
Crédits : Équipe ETS METADIDOMI — conception et développement.

---
