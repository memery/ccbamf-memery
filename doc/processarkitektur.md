Processarkitektur
=================

    Master (1)
      |
      +--- IRC (2)
      |     |
      |     +--- Uppkoppling till Efnet
      |     +--- Uppkoppling till gfu
      |
      +--- Logger (3)
      |
      +--- memery (4)
             |
             +--- URL print för långsam sida
             +--- Lång markov-beräkning
             +--- Snabb .choose-beräkning

Masterprocessen spawnar en IRC-del som ansvarar för ircpruttokollet,
en logger som accepterar meddelanden som den loggar, och en memery
som innehåller allt beteende i boten.

Memeryn ska vara protokollsagnostisk i den mån det går. Adminfunktioner
relaterade till IRC (stfu, op och sånt) ska probably ligga i uppkopplings-
processerna. Uppkopplingsprocesserna skickar vidare sin input till IRC-
processen som tolkar enligt ircparser, och sen skickar vidare till
memery och logger.

IRC-processen har ansvar för uppkopplingsprocesserna, och ser därför till
att starta om dem om de får allvarliga fel i sig.

Logger-processen tar emot protokollagnostiska meddelanden och loggar dem
(här kommer ett problem! logger kan inte logga OPs och stfu:n och sånt
om logger är protokollagnostisk! aaaaa)

Memery-processen tar liksom logger-processsen emot protokollagnostiska
meddelanden och skickar ev svar tillbaks. Memeryprocessen kan också skicka
meddelanden på eget initiativ, till exempel markov och sånt!

IRC-processen tar emot protokollagnostiska meddelanden, konverterar med
ircparser och dispatchar dem till rätt uppkopplingsprocess som skriver ut
dem.

Om logger startas om av master måste det meddelas till IRC (tror jag?)
så att den kan uppdatera sig med nya addressen till logger. Om memery
startas om måste memery ansvara för att stänga sina processer (?)
och sen ska ny address till memery meddelas till IRC.

