# Compte-rendu - TP4 Sécurité dans l'usine logicielle

**Auteur :** Binôme d'étudiants M1 DevOps (Sup de Vinci)

## Partie 0 — État des lieux

J'ai commencé par vérifier que le projet est bien structuré et que les outils de qualité (black, ruff, bandit, semgrep, pytest) sont déjà présents dans le `requirements.txt` conformément aux prérequis du TP3. J'ai également corrigé la configuration de `ruff` pour ignorer les alertes `assert` dans les tests.

## Partie 1 — Scan de dépendances avec pip-audit

### 1.1 et 1.2 — Expérimentation locale
J'ai testé `pip-audit` sur notre projet. Bien que quelques vulnérabilités mineures soient présentes dans l'environnement global, l'outil est très efficace. En simulant une vulnérabilité avec `flask==2.0.0`, j'ai pu observer que l'outil identifie précisément la version fautive, l'ID de la vulnérabilité (CVE/GHSA) et les versions de correction (2.2.5 ou 2.3.2).

### Questions
**Question 1 : Qu'est-ce qu'une CVE ? Expliquez le score CVSS et donnez un exemple de CVE avec son impact.**

*   **CVE (Common Vulnerabilities and Exposures) :** C'est un dictionnaire de vulnérabilités de sécurité informatique rendu public. Chaque entrée (ex: CVE-2023-30861) décrit une faille spécifique dans un logiciel ou un matériel.
*   **Score CVSS (Common Vulnerability Scoring System) :** C'est un système de notation (de 0 à 10) qui permet d'évaluer la sévérité d'une vulnérabilité. Il prend en compte des critères comme la facilité d'exploitation, l'impact sur la confidentialité, l'intégrité et la disponibilité des données.
*   **Exemple :** La CVE-2023-30861 dans Flask (CVSS 7.5). Elle permettait une fuite de cookies de session via des serveurs proxy de mise en cache.

**Question 2 : Pourquoi est-il important de scanner les dépendances et pas seulement votre propre code ?**

Il est crucial de scanner les dépendances car une application moderne repose majoritairement sur du code tiers. On parle de **sécurité de la "Supply Chain"**. Même si mon propre code est sécurisé, une bibliothèque vulnérable (comme Flask ou Requests) peut offrir un point d'entrée aux attaquants.

## Partie 2 — Dependabot : mises à jour automatiques

J'ai configuré Dependabot pour automatiser la surveillance et la mise à jour de nos dépendances Python et de nos Actions GitHub.

### Question
**Question 3 : Quel est l'avantage de Dependabot par rapport à un scan manuel avec pip-audit ? Pourquoi configure-t-on aussi l'écosystème github-actions ?**

*   **Avantage :** Dependabot est un outil de **remédiation proactive**. Il crée automatiquement des Pull Requests pour appliquer les correctifs, là où `pip-audit` ne fait que de la détection.
*   **GitHub Actions :** Les actions sont aussi des composants tiers qui peuvent présenter des failles ; il est donc essentiel de les maintenir à jour.

## Partie 3 — Gestion des secrets avec GitHub Secrets

J'ai intégré l'utilisation des secrets GitHub pour éviter de stocker des informations sensibles en dur dans le code.

### Question
**Question 4 : Pourquoi ne doit-on jamais mettre un secret directement dans le code source ? Citez 3 endroits où stocker des secrets de manière sécurisée.**

*   **Risque :** Un secret en dur est exposé à toute personne ayant accès au dépôt et reste dans l'historique Git même après suppression.
*   **3 endroits sécurisés :** Gestionnaires de secrets (GCP Secret Manager), Secrets de plateforme (GitHub Secrets), Variables d'environnement locales (.env ignoré).

## Partie 4 — Détection de secrets avec GitLeaks

J'ai intégré GitLeaks pour scanner l'historique et les commits à la recherche de secrets exposés.

### Questions
**Question 5 : Un développeur a accidentellement commité une clé API GCP dans le code, puis l'a supprimée dans un commit suivant. Le secret est-il en sécurité ? Que faut-il faire ?**

*   **Sécurité :** Non, le secret reste dans l'historique Git.
*   **Actions :** Révoquer le secret immédiatement, nettoyer l'historique (BFG, filter-repo) et générer une nouvelle clé.

**Question 6 : Pourquoi GitLeaks est-il placé au tout début du pipeline, avant même le linting ?**

Pour appliquer le principe du **fail-fast** : une fuite de secret doit stopper immédiatement toute la chaîne pour éviter de propager le risque.

## Partie 5 — Pipeline de sécurité complet

Le pipeline final intègre désormais : GitLeaks, Black, Ruff, pip-audit, Bandit, Semgrep, Pytest et SonarCloud.

### Questions
**Question 7 : Citez 3 risques de l'OWASP Top 10 et expliquez comment votre pipeline CI les adresse (ou pas).**

*   **A06:2021 – Composants vulnérables :** Adressé par `pip-audit`.
*   **A03:2021 – Injection :** Adressé par `Bandit` et `Semgrep`.
*   **A01:2021 – Contrôle d'accès défaillant :** Testé via `Pytest`.

**Question 8 : Décrivez l'ordre complet de votre pipeline final. Pour chaque étape, indiquez quel type de problème elle détecte.**

1. GitLeaks (Secrets), 2. Black (Formatage), 3. Ruff (Linting), 4. pip-audit (SCA), 5. Bandit (SAST Python), 6. Semgrep (SAST Multi), 7. Pytest (Tests/Couverture), 8. SonarCloud (Qualité globale).

**Question 9 : Comparez les approches Shift Left et audit de sécurité traditionnel. Quels sont les avantages du Shift Left ?**

Le Shift Left intègre la sécurité dès le début (CI). Avantages : corrections moins chères, détection précoce, autonomie des développeurs.

**Question 10 : Si le temps d'exécution devenait trop long, comment pourriez-vous l'optimiser ?**

Parallélisation des jobs, scan incrémental (uniquement fichiers modifiés), utilisation de cache agressif.

## Partie 6 — Recherche autonome

### 6.1 — Recherche d'une CVE Flask
J'ai identifié la **CVE-2023-30861** (GHSA-68rp-wp8r-4726).
*   **Impact :** Fuite de cookies de session.
*   **Correction :** Version 3.1.3. `pip-audit` aurait bloqué le pipeline sur une version antérieure.

### 6.2 — Sécurisation d'une route Flask
J'ai implémenté l'ajout de **headers de sécurité** (X-Content-Type-Options, X-Frame-Options, CSP) via un hook `@app.after_request` pour protéger l'application contre le Clickjacking et les attaques XSS.
