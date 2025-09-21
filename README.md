
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

Metadidomi Server Plus s’adapte à vos besoins : mode développement pour tester, mode production pour sécuriser. Les interfaces web sont accessibles depuis n’importe quel appareil, et l’application Windows vous offre une prise en main immédiate.

---

## 🔒 Sécurité et sérénité

Votre cloud, vos règles. Authentification par clé, tokens JWT, CORS strict, et la possibilité d’ajouter un reverse proxy HTTPS pour une tranquillité absolue.

---

## ✨ Fonctionnalités clés (détail technique)

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

## 💡 Guide rapide d'installation (exemples)

### Prérequis

* Windows 7 et plus
* Accès administrateur pour ouvrir des ports

### Installation rapide (Windows - exemple)

```powershell
# Lancer le service (exemple .exe)
Suivez les instructions d'installation"

# Les ports 8000/5000/8100 doivent etre disponible dans le pare-feu
New-NetFirewallRule -DisplayName "Metadidomi HTTP" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
```
## 🔧 Utilisation minimale

* **Demarrer toujours un serveur avant d'acceder à son IU, si la page ne s'affiche pas reactualiser plusieurs fois la page, il est possible que le deamarrage du serveur prenne un peu de temps.
* **Le bouton Main UI est considéré comme la page d'acceuil pour acceder à d'autres pags.

---
## 🔧 AMELIORATION AVENIR

* **La creation de compte utilisateur dans la section "utilisateur" presente encore des disfonctionneent.
* **La suppression des dossiers dans le "Cloud Storage" ne fonctionne pas encore. Faites nous par de tout disfonctionnement observer nous y travaillerons aussi rapidement que possible.

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

---
| Pays                | Éligible |
|----------------------|-----------|
| Bénin               | ✅        |
| Burkina Faso        | ✅        |
| Cameroun            | ✅        |
| Congo               | ✅        |
| Côte d'Ivoire       | ✅        |
| Gabon               | ✅        |
| Kenya               | ✅        |
| République du Congo | ✅        |
| Rwanda              | ✅        |
| Sénégal             | ✅        |
| Tanzanie            | ✅        |
| Zambie              | ✅        |

---

## ✉️ Contact

**Essayez Metadidomi Server Plus dès aujourd’hui et faites entrer le cloud chez vous.**
Contact : [infos.contact.metadidomi@gmail.com](mailto:infos.contact.metadidomi@gmail.com)

---

## 🧾 Licence & crédits

Distribué sous la licence Closed Source.
Crédits : Équipe ETS METADIDOMI — conception et développement.

---
