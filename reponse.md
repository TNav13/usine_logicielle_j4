# Compte-rendu - TP4 Sécurité dans l'usine logicielle

## Questions
**Question 1 : Qu'est-ce qu'une CVE ? Expliquez le score CVSS et donnez un exemple de CVE avec son impact.**

*   **CVE (Common Vulnerabilities and Exposures) :** C'est un dictionnaire de vulnérabilités de sécurité informatique rendu public. Chaque entrée (ex: CVE-2023-30861) décrit une faille spécifique dans un logiciel ou un matériel.
*   **Score CVSS (Common Vulnerability Scoring System) :** C'est un système de notation (de 0 à 10) qui permet d'évaluer la sévérité d'une vulnérabilité. Il prend en compte des critères comme la facilité d'exploitation, l'impact sur la confidentialité, l'intégrité et la disponibilité des données.
*   **Exemple :** La CVE-2023-30861 dans Flask (CVSS 7.5). Elle permettait une fuite de cookies de session via des serveurs proxy de mise en cache.

**Question 2 : Pourquoi est-il important de scanner les dépendances et pas seulement votre propre code ?**

Il est crucial de scanner les dépendances car une application moderne repose majoritairement sur du code tiers. On parle de **sécurité de la "Supply Chain"**. Même si mon propre code est sécurisé, une bibliothèque vulnérable (comme Flask ou Requests) peut offrir un point d'entrée aux attaquants.

**Question 3 : Quel est l'avantage de Dependabot par rapport à un scan manuel avec pip-audit ? Pourquoi configure-t-on aussi l'écosystème github-actions ?**

*   **Avantage :** Dependabot est un outil de **remédiation proactive**. Il crée automatiquement des Pull Requests pour appliquer les correctifs, là où `pip-audit` ne fait que de la détection.
*   **GitHub Actions :** Les actions sont aussi des composants tiers qui peuvent présenter des failles ; il est donc essentiel de les maintenir à jour.

**Question 4 : Pourquoi ne doit-on jamais mettre un secret directement dans le code source ? Citez 3 endroits où stocker des secrets de manière sécurisée.**

*   **Risque :** Un secret en dur est exposé à toute personne ayant accès au dépôt et reste dans l'historique Git même après suppression.
*   **3 endroits sécurisés :** Gestionnaires de secrets (GCP Secret Manager), Secrets de plateforme (GitHub Secrets), Variables d'environnement locales (.env ignoré).

**Question 5 : Un développeur a accidentellement commité une clé API GCP dans le code, puis l'a supprimée dans un commit suivant. Le secret est-il en sécurité ? Que faut-il faire ?**

*   **Sécurité :** Non, le secret reste dans l'historique Git.
*   **Actions :** Révoquer le secret immédiatement, nettoyer l'historique (BFG, filter-repo) et générer une nouvelle clé.

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
