Hotswapping av processer
========================

IRC-uppkopplings-processerna kan skicka meddelande om `Reload('irc_connection')`
till IRC-processen, i vilken en flagga tänds som indikerar att vid nästa reconnect
ska också reload göras. (Kan reload göras direkt utan att påverka nuvarande
funktioner? Borde kanske gå.) Det är dumt att reconnecta automagiskt vid reload,
för om båten fyller en vital funktion i någon kanal (detta blir lurigt över flera
kanaler på samma nätverk...) så kanske man borde avgöra separat när den ska
återansluta och ladda om.

Om meddelandet istället är att `Reload('irc')` så måste irc spara sin barn, skicka
dem i ett meddelande till master, som startar om irc och ger den barnen tillbaks,
antingen direkt som argument eller via någon slags meddelande. Ahduno. IRC-
processen bör även få fortsätta använda samma inbox som tidigare, eller?

Om meddelandet är `Reload('master')` så hf.

Om meddelandet är `Reload('logger')` så ska IRC skicka meddelande till logger om
att logger ska spara det den håller på med och sen be om att få startas om, efter
vilket den kan startas om *med samma inbox som den hade sen tidigare*! Detta för
att saker inte ska försvinna ut i cyberrymden medan den startar om, utan när den
är klar återupptar den bara där den slutade.

Om meddelandet är `Reload('memery')` så ska IRC skicka meddelande till memery om
att memery ska be om att få bli omstartad och sedan bara dö ut när nuvarande
beräkningar är klara. Nya memery kan gott använda samma inbox som gamla, bara
inte gamla får någon chans att läsa in saker från den på nytt innan den dör ut.

Viktiga punkter:

 *  Ingen process får döda sina barn! Processen kan be sina barn om att stänga av
    eller starta om, men barnen själva får fatta slutgiltiga beslutet för de har
    bättre koll på läget.

 *  Vissa processer måste när de startas om ta över sin gamla inbox för att inte
    viktig information ska gå förlorad.

 *  För att kunna ladda om IRC utan att tappa uppkopplingarna krävs det att IRC
    sparar sina barn så att nästa IRC kan ta över dem, utan att behöva starta nya.
