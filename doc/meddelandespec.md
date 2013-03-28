Meddelandespecifikation
=======================

Protokollagnostiska meddelanden behöver följande element:

 1. `process`: vilken process kom meddelandet ifrån? detta kan vara
    typ "efnet," eller "msn." Denna används även för att veta var
    meddelanden från memery ska till!
 2. `source`: var kom meddelandet från inom denna process? Detta
    motsvarar kanalnamn i IRC eller konversationsID av något slag
    i MSN.
 3. `author`: vem skrev det här meddelandet? Detta kan användas för
    att till exempel namenudgea personen som skriver ett kommando
    eller något i IRC, eller bara göra interaktionen lite mer
    personlig.
 4. `content`: faktiskta innehållet i meddelandet.

Detta var mindre komplicerat än jag trodde från början. Det kan finnas
plats för någon form av närvarospårning för protokoll som stödjer det,
till exempel MSN, IRC och XMPP. Detta skulle motsvara joins/quits/parts
i IRC.

 1. `process`: från vilken process kom denna signal?
 2. `source`: var i denna process uppkom signalen?
 3. `author`: vem gjorde denna signal relevant?
 4. `present`: är denna person fortfarande närvarande? (Om denna är True
    innebär det att personen joinade, om den är False innebär det att
    personen partade/quittade.)

Detta är inte fullkomligt protokollsagnostiskt (vissa protokoll stödjer
inte närvarospårning, men se hur mycket jag bryr mig. De flesta
protokoll stödjer det.)

Ett problem med närvarospårning i IRC är att IRC-parsern måste förvandla
quitmeddelanden till parts i alla kanaler där den lämnande användaren
var online, för att undvika en läckande abstraktion. Detta kan göra allt
väldigt mycket mer komplicerat, eftersom IRC-parsern då måste veta i vilka
kanaler som användaren var online... Det kan vara en bra idé att skippa
nävarospårning tills någon Smart Lösning™ finns.
