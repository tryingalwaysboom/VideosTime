# Parte 1 "Los 30 días de Mateo". (id, voz, texto TTS, subtítulo con *palabras clave*)
VOCES = {
    "N": "zl7szWVBXnpgrJmAalgz",   # narradora (Lily - Spanish Storyteller, latina)
    "K": "tTdCI0IDTgFa2iLQiWu4",   # Mateo (Daniela - Cute Storyteller, subida de tono)
    "A": "aYQAm4rWuigkeuRA5i92",   # abuela Pilar (Grandma Aurora)
    "P": "HRi5Prm2B3PevwpDmVLP",   # maestra Marta (María Blanco)
}
LINEAS = [
 ("F01","N","[tense] Abres la mochila de Mateo… y encuentras una nota de la maestra. En rojo. Quédate hasta el final, porque lo que pase después… lo decides tú.",
  "Abres la *mochila* de Mateo… y encuentras una *nota* de la *maestra.* En *rojo.* Quédate hasta el *final,* porque lo que pase después… lo *decides* *tú.*"),
 ("F02","P","[serious] Mamá de Mateo: es el único del salón que todavía no escribe su nombre. Si no lo logra antes de fin de año… tendremos que hablar de que repita.",
  "Mamá de Mateo: es el *único* del salón que todavía *no* *escribe* su *nombre.* Si no lo logra antes de *fin* *de* *año…* tendremos que hablar de que *repita.*"),
 ("F03","N","Lo lees tres veces. Y justo vibra el celular: en el grupo de mamás, la mamá de Sofía presume que su hija ya escribe su nombre completo… con apellido.",
  "Lo lees *tres* *veces.* Y justo vibra el *celular:* en el *grupo* de *mamás,* la mamá de *Sofía* presume que su hija ya escribe su nombre *completo…* con *apellido.*"),
 ("F04","N","Mateo tiene cuatro años y medio. Llena las paredes de dinosaurios. Pero cada vez que ve un lápiz… se esconde.",
  "Mateo tiene *4* *años* y *medio.* Llena las paredes de *dinosaurios.* Pero cada vez que ve un *lápiz…* se *esconde.*"),
 ("F05","N","Esa tarde lo sientas en la mesa de la cocina. Le escribes su nombre arriba, grande: eme, a, te, e, o.",
  "Esa tarde lo sientas en la mesa de la *cocina.* Le escribes su *nombre* arriba, *grande:* *M,* *A,* *T,* *E,* *O.*"),
 ("F06","K","[whining] ¿Otra vez la tarea? ¡No quiero! ¡Me aburro!",
  "¿Otra vez la *tarea?* ¡No *quiero!* ¡Me *aburro!*"),
 ("F07","N","Le pones el lápiz en la mano. Aprieta tan fuerte… que la punta se rompe.",
  "Le pones el *lápiz* en la mano. Aprieta tan *fuerte…* que la punta se *rompe.*"),
 ("F08","K","[crying] ¡¿Ves?! ¡Yo no sé! ¡Yo no sé escribir!",
  "*¡¿Ves?!* ¡Yo *no* *sé!* ¡Yo no sé *escribir!*"),
 ("F09","N","Se va corriendo a su cuarto. En la hoja queda una sola letra: una eme torcida… y al revés.",
  "Se va *corriendo* a su cuarto. En la hoja queda una *sola* *letra:* una *M* *torcida…* y al *revés.*"),
 ("F10","N","Suena el timbre. Es tu mamá, la abuela Pilar. Ve la hoja sobre la mesa… y suspira.",
  "Suena el *timbre.* Es tu mamá, la abuela *Pilar.* Ve la *hoja* sobre la mesa… y *suspira.*"),
 ("F11","A","[disapproving] Ay, mija. En mis tiempos, a los cinco años ya escribíamos en cursiva. A ese niño le falta mano dura.",
  "Ay, *mija.* En mis *tiempos,* a los *5* *años* ya escribíamos en *cursiva.* A ese niño le falta *mano* *dura.*"),
 ("F12","N","Te muerdes la lengua. Esa noche, cuando por fin se duerme, buscas en el celular: mi hijo no quiere escribir. Mil consejos. Todos distintos.",
  "Te muerdes la *lengua.* Esa *noche,* cuando por fin se duerme, buscas en el celular: mi hijo *no* *quiere* *escribir.* *Mil* *consejos.* Todos *distintos.*"),
 ("F13","N","[tense] Día dos. Desayuno. Lo intentas otra vez. Mateo empuja el cuaderno… y el vaso de leche cae encima de la hoja.",
  "*Día* *2.* *Desayuno.* Lo intentas *otra* *vez.* Mateo *empuja* el cuaderno… y el vaso de *leche* cae *encima* de la hoja."),
 ("F14","K","[angry, crying] ¡Ya no quiero hacer letras nunca! ¡Las letras son feas!",
  "¡Ya no quiero hacer letras *nunca!* ¡Las letras son *feas!*"),
 ("F15","N","[sad] Y le gritas. Más fuerte de lo que querías. Mateo se queda callado… con los ojos llenos de lágrimas.",
  "Y le *gritas.* Más *fuerte* de lo que querías. Mateo se queda *callado…* con los ojos llenos de *lágrimas.*"),
 ("F16","N","[sad] Te sientas en el piso de la cocina. Dos días. Y ni una letra.",
  "Te sientas en el *piso* de la cocina. *Dos* *días.* Y ni *una* *letra.*"),
 ("F17","N","[softly] Entonces Mateo vuelve, despacito. Trae su dinosaurio… y una crayola verde.",
  "Entonces Mateo *vuelve,* *despacito.* Trae su *dinosaurio…* y una *crayola* *verde.*"),
 ("F18","K","[shy, softly] Mami… ¿el Rex puede tener nombre también?",
  "*Mami…* ¿el *Rex* puede tener *nombre* también?"),
 ("F19","N","Tienes dos caminos. A: mano dura, como dice la abuela: sin tablet hasta que llene una hoja entera de emes. B: guardas el cuaderno y hoy escriben juntos el nombre del dinosaurio… aunque pierdas otro día.",
  "Tienes *dos* *caminos.* *A:* *mano* *dura,* como dice la abuela: sin *tablet* hasta que llene una hoja entera de *M.* *B:* guardas el *cuaderno* y hoy escriben juntos el nombre del *dinosaurio…* aunque pierdas *otro* *día.*"),
 ("F20","N","Vota en la encuesta… y dime en comentarios por qué. Lo que elijan, pasará.",
  "*Vota* en la *encuesta…* y dime en *comentarios* por *qué.* Lo que elijan, *pasará.*"),
]
