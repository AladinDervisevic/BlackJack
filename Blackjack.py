import model
import bottle

blackjack = model.Blackjack()

bottle.run(reloader = True, debug = True)