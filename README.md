# VHDL_Centroids_Test
Repo temporanea contenente lo script necessario per blackbox-testing.
## Utilizzo
L'utilizzo dello script in python, al fine della creazione di test con molteplici dati di input, necessita l'utilizzo della seguente funzione,:
```
create_seq_tbenchs(list_n_mask_1, list_min_same_distance, list_distance, n_tests, filename)
 ```
 dove: 
 
 - list_n_mask_1 è la lista con il minimo di 1 presenti nella maschera di ingresso.
 - list_min_same_distance è la lista con il minimo numero di 1 nella maschera d'uscita.
 - list_distance è la lista con le distanze minime.
 - n_tests è il numero di test, uguale alla size() degli argomenti
 - filename è il nome del file

Lo script in TCL, con le dovute modifiche (occorre cambiare il nome del simulation set e il numero di test), può essere runnato attraverso la seguende linea di comando (è necessario avere vivado accessibile da $PATH):
```
vivado -mode tcl -source testcentroids.tcl -verbose project_reti_logiche.xpr
```
Sarà possibile visionare il log successivamente in vivado.log
