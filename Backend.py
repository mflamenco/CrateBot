import flask
from flask.json import jsonify
import uuid
from createBotSim import Bot, Crate, Warehouse

crateBotSim = {}
app = flask.Flask(__name__)

@app.route("/crateBotSim", methods=["POST"])
def create():
    global crateBotSim
    id = str(uuid.uuid4())
    crateBotSim[id] = Warehouse()
    return "ok", 201, {'Location': f"/crateBotSim/{id}"}

@app.route("/crateBotSim/<id>", methods=["GET"])
def queryState(id):
    global model
    model = crateBotSim[id]
    model.step()
    agents = model.schedule.agents

    bList = []
    cList = []
    pList = model.pList

    for agent in agents:
        if(isinstance(agent, Bot)):
            bList.append({"id": agent.unique_id, "x": agent.pos[0], "y": agent.pos[1], "occupied": agent.occupied})
        elif(isinstance(agent, Crate)):
            cList.append({"id": agent.unique_id, "x": agent.pos[0], "y": agent.pos[1], "active": agent.active})

    return jsonify({"bots": bList, "crates": cList, "piles": pList})

app.run()
