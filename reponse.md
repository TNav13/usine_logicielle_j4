# Compte-rendu - TP4 Sécurité dans l'usine logicielle

**Auteur :** Binôme d'étudiants M1 DevOps (Sup de Vinci)

## Partie 1 — Scan de dépendances avec pip-audit

### 1.1 et 1.2 — Expérimentation locale
J'ai testé `pip-audit` sur notre projet. Bien que quelques vulnérabilités mineures soient présentes dans l'environnement global, l'outil est très efficace. En simulant une vulnérabilité avec `flask==2.0.0`, j'ai pu observer que l'outil identifie précisément la version fautive, l'ID de la vulnérabilité (CVE/GHSA) et les versions de correction (2.2.5 ou 2.3.2).

### Questions
**Question 1 : Qu'est-ce qu'une CVE ? Expliquez le score CVSS et donnez un exemple de CVE avec son impact.**

*   **CVE (Common Vulnerabilities and Exposures) :** C'est un dictionnaire de vulnérabilités de sécurité informatique rendu public. Chaque entrée (ex: CVE-2023-30861) décrit une faille spécifique dans un logiciel ou un matériel.
*   **Score CVSS (Common Vulnerability Scoring System) :** C'est un système de notation (de 0 à 10) qui permet d'évaluer la sévérité d'une vulnérabilité. Il prend en compte des critères comme la facilité d'exploitation, l'impact sur la confidentialité, l'intégrité et la disponibilité des données. Un score au-dessus de 7.0 est généralement considéré comme critique ou élevé.
*   **Exemple :** La CVE-2023-30861 dans Flask (CVSS 7.5). Elle permettait une fuite de cookies de session via des serveurs proxy de mise en cache, ce qui pouvait permettre à un attaquant de voler une session utilisateur.

**Question 2 : Pourquoi est-il important de scanner les dépendances et pas seulement votre propre code ?**

Il est crucial de scanner les dépendances car une application moderne repose majoritairement sur du code tiers (bibliothèques open-source). On parle de **sécurité de la "Supply Chain"**. Même si mon propre code est parfaitement sécurisé, si une bibliothèque que j'utilise (comme Flask ou Requests) possède une faille connue, mon application devient vulnérable. Les attaquants ciblent souvent ces dépendances populaires car elles offrent un point d'entrée sur de très nombreux systèmes simultanément.

## Partie 2 — Dependabot : mises à jour automatiques

J'ai configuré Dependabot pour automatiser la surveillance et la mise à jour de nos dépendances Python et de nos Actions GitHub.

### Question
**Question 3 : Quel est l'avantage de Dependabot par rapport à un scan manuel avec pip-audit ? Pourquoi configure-t-on aussi l'écosystème github-actions ?**

*   **Avantage de Dependabot :** Contrairement à `pip-audit` qui est un outil de détection (il nous dit ce qui ne va pas), Dependabot est un outil de **remédiation proactive**. Il surveille les dépôts en continu et, dès qu'une mise à jour (de sécurité ou non) est disponible, il crée automatiquement une Pull Request avec les changements nécessaires. Cela réduit la "dette de sécurité" sans intervention manuelle constante.
*   **Écosystème github-actions :** Les Actions GitHub que nous utilisons sont aussi des logiciels tiers qui peuvent avoir des vulnérabilités ou devenir obsolètes. Les scanner permet de s'assurer que notre infrastructure de CI/CD est toujours basée sur des versions stables et sécurisées.

## Partie 3 — Gestion des secrets avec GitHub Secrets

J'ai intégré l'utilisation des secrets GitHub pour éviter de stocker des informations sensibles en dur dans le code.

### Question
**Question 4 : Pourquoi ne doit-on jamais mettre un secret directement dans le code source ? Citez 3 endroits où stocker des secrets de manière sécurisée.**

*   **Pourquoi pas en dur ?** Si un secret est dans le code source, toute personne ayant accès au dépôt (même en lecture) peut le voir. Si le dépôt est public, il est exposé au monde entier. De plus, une fois commités, les secrets restent dans l'historique Git même si on les supprime plus tard. Des outils automatisés scannent en permanence GitHub à la recherche de clés API fuyant ainsi.
*   **3 endroits sécurisés :**
    1.  **Gestionnaires de secrets (Vaults) :** HashiCorp Vault, AWS Secrets Manager, GCP Secret Manager.
    2.  **Secrets de plateforme CI/CD :** GitHub Secrets, GitLab CI/CD Variables.
    3.  **Variables d'environnement locales :** Chargées via un fichier `.env` (exclu du commit via `.gitignore`) ou configurées sur le serveur d'exécution.

## Partie 4 — Détection de secrets avec GitLeaks

J'ai testé GitLeaks localement et simulé une fuite de secret. L'outil a parfaitement détecté la clé API GCP factice.

### Questions
**Question 5 : Un développeur a accidentellement commité une clé API GCP dans le code, puis l'a supprimée dans un commit suivant. Le secret est-il en sécurité ? Que faut-il faire ?**

*   **Sécurité :** Non, le secret n'est pas en sécurité. Il reste présent dans l'historique Git et peut être récupéré par n'importe qui ayant accès au dépôt.
*   **Actions à mener :** Il faut impérativement révoquer (invalider) le secret immédiatement auprès du fournisseur, puis nettoyer l'historique Git (avec `BFG` ou `git-filter-repo`) et enfin générer une nouvelle clé.

**Question 6 : Pourquoi GitLeaks est-il placé au tout début du pipeline, avant même le linting ?**

Pour appliquer le principe du **fail-fast**. La détection d'un secret est une faille de sécurité majeure qui doit stopper immédiatement le pipeline pour éviter de propager le risque et pour économiser des ressources de calcul inutiles sur un commit qui de toute façon sera rejeté.

## Partie 5 — Pipeline de sécurité complet

J'ai assemblé le pipeline final intégrant toutes les couches de sécurité et de qualité. J'ai également mis à jour le fichier `.gitignore` pour exclure les rapports générés.

### Questions
**Question 7 (compte-rendu) : Citez 3 risques de l'OWASP Top 10 et expliquez comment votre pipeline CI les adresse (ou pas).**

*   **A06:2021 – Composants vulnérables et obsolètes :** Adressé par `pip-audit` et `Dependabot`.
*   **A03:2021 – Injection :** Adressé par `Bandit` et `Semgrep` qui détectent les injections SQL ou de commandes.
*   **A07:2021 – Échecs d'identification et d'authentification :** Adressé partiellement par nos tests unitaires qui valident la logique métier.

**Question 8 (compte-rendu) : Décrivez l'ordre complet de votre pipeline final. Pour chaque étape, indiquez quel type de problème elle détecte.**

1.  **GitLeaks :** Détecte les secrets (clés API, mots de passe) commités.
2.  **Black :** Problèmes de formatage.
3.  **Ruff :** Mauvaises pratiques de codage et bugs potentiels.
4.  **pip-audit :** Vulnérabilités connues (CVE) dans les dépendances.
5.  **Bandit :** Failles de sécurité spécifiques au langage Python (SAST).
6.  **Semgrep :** Patterns de code dangereux et conformité (SAST).
7.  **Pytest :** Erreurs fonctionnelles et mesure de la couverture de tests.
8.  **SonarCloud :** Analyse globale de la qualité, sécurité et dette technique.

**Question 9 (compte-rendu) : Comparez les approches Shift Left et audit de sécurité traditionnel. Quels sont les avantages du Shift Left ?**

L'audit traditionnel se fait en fin de cycle de développement, ce qui rend les corrections coûteuses et tardives. Le **Shift Left** déplace ces contrôles au plus tôt dans le cycle (dès le commit).
*   **Avantages :** Corrections moins coûteuses, meilleure qualité de code dès le départ, réduction du temps de mise sur le marché (Time to Market) et autonomisation des développeurs sur la sécurité.

**Question 10 (compte-rendu) : Votre pipeline contient maintenant de nombreuses étapes. Si le temps d'exécution devenait trop long, comment pourriez-vous l'optimiser ?**

1.  **Parallélisation :** Exécuter les outils de scan (SAST) simultanément.
2.  **Scan incrémental :** Ne scanner que les fichiers modifiés.
3.  **Cachage :** Utiliser des caches persistants pour les dépendances et les résultats intermédiaires.
4.  **Infrastructure :** Utiliser des runners plus puissants ou des images Docker optimisées.
