from projectq.ops import All, CNOT, H, Measure, X, Z
from projectq import MainEngine

def main():
    quantum_engine = MainEngine()

    # information we want to transmit
    information_to_transmit = 1

    # this qubit is the senders qubit
    qubit_one = quantum_engine.allocate_qubit()

    # the receivers qubit
    qubit_two = quantum_engine.allocate_qubit()

    # create_bell_pair is creating a bell-pair
    # a bell pair resembles two qubits two entangled by a CNOT gate
    # thereby the input qubit is set to a superposition (done by the Hadamard gate)
    # This results in two qubits with a correlatable value (if additional information is given)
    # the additional information in this case is the classical_encoded_message variable which
    # holds data about the  first measurement from the sender
    qubit_one, qubit_two = create_bell_pair(quantum_engine, qubit_one, qubit_two)

    print('Information that is transmitted: ',information_to_transmit)

    # preparing the senders qubits and collapsing their state(measuring them) so that information can be send to the receiver
    classical_encoded_message = init_sender_qubits(quantum_engine=quantum_engine, qubit_one=qubit_one, message_value = information_to_transmit)
    print('Prepared and measured qubits in classical message: ', classical_encoded_message)

    # Sending the message along with the second qubit for state re-creation
    recieved_bit = read_receiver_qubit(quantum_engine, classical_encoded_message,qubit_two)

    print('Received bit: ', recieved_bit)


def create_bell_pair(quantum_engine, qubit_one='', qubit_two=''):
    # Hadamard gate to put Qubit one in superposition
    # This sets the value of a equal probability of being 1 or 0
    H | qubit_one


    # CNOT gate to flip the second Qubit conditionally
    # on the first qubit being in the state |1⟩
    CNOT | (qubit_one, qubit_two)

    return qubit_one, qubit_two


def init_sender_qubits(quantum_engine='',qubit_one='', message_value = 0):
    # this qubit "encodes" the information we want to transmit(message_value)
    qubit_encoding_information = quantum_engine.allocate_qubit()

    # if the message_value is (bianry) 1 the qubits qubit_encoding_information state is flipped with a X-Gate
    if message_value == 1:
        X | qubit_encoding_information


    # entangling the senders(qubit_one) qubit with the qubit that encodes the inforamtion(qubit_encoding_information) we want to transmit
    CNOT | (qubit_encoding_information, qubit_one)


    # the message qubit is set to superposition (by applying the Hadamard-Gate)
    H | qubit_encoding_information

    # both, the information encoding qubit(qubit_encoding_information) and the qubits are measured
    # the resulting effect is that the senders qubits (qubit_one) state may change (thorugh the CNOT-Gate applied above)
    Measure | qubit_encoding_information
    Measure | qubit_one

    # since both qubits are measured they now have definit and readable values which are sent to the receiver (thourgh classical channels)
    classical_encoded_message = [int(qubit_encoding_information), int(qubit_one)]

    return classical_encoded_message


def read_receiver_qubit(quantum_engine,message,qubit_two):

    # if the measured qubit, qubit_encoding_information has value 1 a X-Gate is applied to the receivers qubit(qubit_two)
    if message[1] == 1:
        X | qubit_two
    # if the measured sender qubit(qubit_one) has value 1 a Z-Gate is applied to the receivers qubit(qubit_two)
    if message[0] == 1:
        Z | qubit_two

    # finally the receivers qubit is measured
    # the result of the measurement is dependent on manipulation above
    # without the manipulation, the result of the receivers qubit measurement would be useless
    # the measurement now is not just dependent on the bell-pair-link(entanglement)
    # (between sender and receiver qubits) which would still not be enough to transmit information
    # but also completed by the information given by the classical channel which completes the transmission process
    Measure | qubit_two

    quantum_engine.flush()

    recieved_information = int(qubit_two)

    return recieved_information

if __name__ == "__main__":
    main()
