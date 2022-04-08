`burnout-sentry` a été réalisé dans le cadre d'un test technique. L'énoncé était le suivant :

> Dans une idée de prévenir les situations de burnout des développeurs, on voudrait produire un rapport reprenant par personne un taux de travail "hors horaires", qu'on définirait comme la part de commits qui sont réalisés le week-end ou avant 8h / après 20h.
> 
> L'exercice est donc l'écriture d'un script Python qui prendrait les données du dépôt d'une de nos applications et afficherait ces taux.

Ce document offre des éléments de contexte sur le processus de réalisation de l'exercice, mes choix et mes raisonnements.

# Analyse du problème et préparation

Aucune autre contrainte n'est définie dans l'énoncé, je choisis donc de consacrer un maximum de 4h à la réalisation. Comme j'ai déjà réalisé des scripts similaires par le passé et que je n'identifie pas a priori de problématiques complexes qui peuvent me ralentir, j'estime qu'il me faudra entre une et deux heures pour obtenir un script fonctionnel qui réponde au besoin énoncé.

Je décide donc de consacrer le temps supplémentaire à améliorer le confort d'utilisation du script et à le rendre utilisable pour le plus grand nombre de cas d'usages possible.

En effet, si les entrées et les sorties du script sont très bien spécifiées, le contexte d'utilisation, lui, ne l'est pas. Qui va le lancer, à quel moment, sur quel jeu de données, dans quel objectif ? Les cas d'utilisations suivants me semblent plausibles :

1. Simon a l'impression que depuis quelques semaines, sa collègue Maria travaille régulièrement pendant son temps de repos. Il préfère s'en assurer avant de vérifier avec elle que tout va bien.
2. Nathalie veut être informée périodiquement et automatiquement (par exemple tous les mois, par mail) des risques de burnout au sein de son équipe afin de détecter au plus tôt des signes inquiétants
3. Nathalie veut décourager le travail sur le temps de repos en bloquant via un hook Git les commits effectués hors des périodes travaillées
4. Maria veut avoir une idée plus claire de son rythme de travail et identifier à quel moment la situation s'est dégradée

Dans les cas 1 et 4, une personne va manuellement appeler le script pour répondre à une question spécifique. Dans les cas 2 et 3, c'est une tâche cron ou un hook git qui va être appelé automatiquement et/ou périodiquement. Dans l'ensemble des cas, les données à utiliser et à présenter vont être différentes :

1. Ce sont les contributions de Maria sur une période récente (X semaines) et le période précédente qui vont servir à analyser la situation
2. Ce sont les contributions de plusieurs personnes, sur un mois (et éventuellement la période précédente, pour comparer) qui vont servir à analyser la situation
3. Ce sont les contributions de la personne qui commit qui vont servir à accepter ou décliner la contribution, sur une période potentiellement plus courte, par exemple 2 semaines
4. Ce sont les les contributions de Maria sur des périodes variables qui vont servir à analyser la situation

Deux filtres permettant de limiter les contributions utilisées me semblent ainsi nécessaires :

- Un filtre par date, pour pouvoir restreindre les résultats à une periode donnée
- Un filtre par contributeur·ice, pour pouvoir restreindre les résultats à une personne donnée

Il me semble également nécessaire que le script puisse gérer des plages de travail différentes. Par exemple, si les jours de repos samedi et dimanche sont hardcodés dans le scripts, on ne détectera pas comme potentiellement problématiques les contributions d'une personne à temps partiel qui est off le vendredi.

Enfin, il me semble que l'intérêt de l'outil est fortement limité si on ne peut analyser qu'un seul dépôt Git à la fois. En effet, il est courant qu'une personne contribue à plusieurs dépôts en parallèle, et seule une vue sur l'ensemble de ces contributions peut produire des informations exploitables.

# Déroulement de l'exercie

## Mise en place (commit 59359c81 à 6990d073)

À ce stade, je cherche principalement à comprendre le problème et à mettre en place mon environnement de développement.

- 10 minutes : réfléchir au cas d'usage et aux utilisations possible du rapport généré par le script
- 10 minutes : création du dépôt git/github et écriture d'une documentation pour le fonctionnement attendu du script
- 10 minutes : création des fichiers nécessaire au packaging python (setup.cfg, dépendances, etc.)
- 5 minutes : rédaction d'un hello world avec click pour vérifier que le paquet est installable et que l'appel du script fonctionne

J'utilise click plutôt qu'argparse pour générer mon interface en ligne de commande car je trouve que click permet de produire des interfaces de meilleures qualité à effort équivalent (typage des arguments, documentation, gestion des erreurs, etc.)

## Implémentation des fonctionnalités principales (commit 0aab8c3e à 22690a9b)

À ce stade, je démarre l'implémentation des fonctionnalités :

- 15 minutes : recherche et lecture afin de trouver une bibliothèque python permettant d'extraire les données d'un dépôt git. Mon choix se porte assez rapidement sur PyDriller, qui semble maintenu et répondre à mon besoin.
- 15 minutes : mise à jour du script pour accepter un ou plusieurs arguments, les passer à PyDriller et vérifier que je suis en mesure de collecter les données dont j'ai besoin.
- 30 minutes : écriture du code d'extraction et d'aggregation des données en vue de générer les rapports
- 5 minutes : affichage très basique des données récoltées

## Itérations, améliorations (commit 9a47ba60 à 5f076855)

À ce stade, le script fonctionne et affiche les données demandées mais ne me parait pas pratique à utiliser ou à adapter. J'entame donc des itérations successives pour l'améliorer et implémenter des fonctionnalités qui me semblent intéressantes :

- 20 minutes : support du tri des résultats (par email, nombre de commits, etc.)
- 15 minutes : affichage des données dans des formats plus pratiques à lire ou à manipuler (markdown, restructured text, JSON). J'utilise pour cela la bibliothèque tabulate, avec laquelle j'ai travaillé à de nombreuses reprises
- 10 minutes : petites améliorations et correctifs d'affichage (arrondis, lisibilité)
- 15 minutes : filtrage basique des résultats par plage de date
- 15 minutes : filtrage basique des résultats par recherche dans l'adresse mail de l'auteur·ice du commit 
- 20 minutes : retrait des valeurs hardcodées liées aux plages horaires de travail, remplacement par des arguments optionnels dans la commande
- 10 minutes : autres correctifs et modifications mineures (logs, déploiment continu)

## Finalisation (commit d893eb78 et suivants)

À ce stade, le script fonctionne, répond au besoin principal exprimé et me semble utilisable dans les contextes d'utilisation que j'ai identifiés. Cela fait plus de trois heures que je travaille sur cet exercie, et je m'approche de la limite que je m'étais fixée en commancant.

Je finalise donc le projet en documentant l'utilisation du script avec de nombreux exemples pour faciliter la prise en main. Je procède également à un certain nombre de tests pour vérifier que le comportement documenté est bien le comportement réel et attendu.

Cette dernière étape me prend environ 30 minutes.

# Retour sur l'exercice

Cet exercice ne m'a pas posé de problème d'implémentation, dans la mesure où j'ai déjà travaillé à plusieurs reprises sur des outils similaires. Finalement, c'est l'extraction et l'aggregation des données depuis les dépôts Git qui a été la plus complexe à écrire, puisque c'est là que se trouvent l'essentiel de l'intelligence et des fonctionnalités (filtrage, tri, notamment). Pour cette raison, j'ai dédié du temps à l'écriture de tests unitaires pour les fonctions correspondantes.

Le peu d'information fournies liées au contexte d'utilisation introduit également un flou (peut-être voulu ;) qui laisse la porte ouverte à des implémentations très différentes. Personnellement, j'ai essayé d'accomoder 3 ou 4 scénarios qui me semblaient plausibles, car cela me semblait à la fois intéressant et réalisable dans le temps que je m'étais fixée.

Bien que cela ne fasse pas strictement partie de l'énoncé, j'ai volontairement consacré du temps au packaging, à la documentation et à l'intégration continue du script, qui me semblent tout aussi important que le script lui même s'il doit être utilisé ou modifié. En conséquence, la structure du projet est possiblement plus complexe que ce qui était attendu.

À une échelle plus large que celle du code, à la fin de cet exercie, je me pose la question de l'efficacité de la métrique choisie pour détecter d'éventuelles situation de burn-out. J'identifie notamment les limites suivantes :

- En se focalisant sur le nombre de commits, on risque de biaiser les résultats : si Maria fait un commit important le vendredi après-midi, puis 6 petits commits juste avant de terminer sa journée de travail pour partir en week-end l'esprit tranquille, son ratio sera de 85%. À l'inverse, si Nathalie fait 6 commits le vendredi dans la journée, puis un commit le vendredi soir, un le samedi et un le dimanche, son ratio sera de 33%, alors que la situation est à mon sens plus grave (toutes les plages de repos ont été travaillées)
- En se focalisant sur les commits, on passe à côté d'autres contributions comme le fait d'ouvrir un ticket ou d'y répondre

Je pense qu'on peut arriver à un résultat plus exploitable avec une métrique différente, basée sur le ratio entre le nombre de plage de repos interrompues et le nombre de plage de repos total. Avec une métrique de ce type, en reprenant l'exemple précédent :

- Sur les trois plages de repos de Maria (vendredi, samedi, dimanche), une a été interrompue pour travailler. Son ratio est donc de 33%.
- Sur les trois plages de repos de Nathalie (vendredi, samedi, dimanche), trois ont été interrompues. Son ratio est donc de 100%.

Une métrique de ce type permet également d'intégrer de manière transparente l'ensemble des contributions d'une personne (commit mais aussi commentaire sur un ticket ou une merge request, revue de code, etc.) sans avoir à changer d'implémentation.

Quoi qu'il en soit, je me suis bien amusée ;)