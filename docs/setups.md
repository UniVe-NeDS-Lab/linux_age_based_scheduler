## 4way3
- 4 different flow sizes
- 4 sets of actors
- 480 sec duration

## 4way4
- 4 different flow sizes
- 1 set of actors
  - total 80 tasks
  - sleep 0.2 secs
  - distribution
    - (.002, '300M'),
    - (.03, '3M',),
    - (.26, '300K'),
    - (1, '30K'),
- 480 sec duration

## 4way5
Same as 4way4, but
- 960 sec duration

## 4way6
Same as 4way5, but
- sleep 0.25 secs

## 4way9
- 100 tasks
- sleep 0.2 secs
- dropped 30k flows 
- flow prob is inversely proportional to size (total data for each class is the same between classes)