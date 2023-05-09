# How to use it

Run the command:
``` sh
docker compose up
```

Docker now compose and compile all the needed packages.

Now go to [localhost](http://localhost/)


# Obiettivi bonus progetto #
- vincoli, 
- trigger,
- transazioni,
- stione ruolo e politiche di autorizzazione,
- sicurezza applicazione(da XSS e SqL injection),
- uso di indici e viste,
- o di Expression language o Orm per dialetto SQL(usare oggetti per fare
query e non scrivere la query sotto forma di stringa, questa parte
aiuta anche per la parte di sicurezza);


# Idee progetto #

* home page


** Not logged

Almeno due pagine:
	
	0- navbar
	1- home con login e register
	2- pagina con ricerche pubblicate/history bar
	3- About us
	4- footbar
	5- pagina log in
	
** 	Logged In
	
	0- avremo 2 applicazioni diverse per valutatori/ricercatori
	1- ricercatori possono registrarsti
	2- valutatori richiesto certificato per essere registrati con quel ruolo
	3- firebase storage google
	
	- Ricercatori
	0- sgravatar 
	1- dashboard(github style), lista di pubblicazioni accetta,rifiutate e in
	   review, /grafico andamento e percentuali/ => da pensarci,
	   notifiche,sezione repository progetti di ricerca che puoi aggiungere
    2- sezione aggiungi pdf e commento

# To do#

- Usare gli ORM per gestire la consistenza dei dati durante le operazioni
  (problemi legati alla sincronizzazione : es. with db.session.begin() as transaction:, LOCK TABLE per le view    )
  o usare le transazioni
- trigger,check constraints
- gestire meglio le view e i refresh
- visualizzare lista progetti del researchers
- Form richiesta progetto
- Form registrazione reviewers
- Table project,comments(sottoclassi),versions,reports,pdf,reviewers con relative  classi per le relazioni M:N
- Modificare mappa concettuale e logica
- Interfaccia reviewers,researchers
- Form report
- Interfaccia chat per la comunicazione tra gli utenti
- finire la Home

