from projectq.ops import All, CNOT, H, Measure, X, Z
from projectq import MainEngine

def main():
    quantum_engine = MainEngine()

    #The bit we want to send
    bit = 1

    # make a Bell-pair
    qubit_one, qubit_two = create_bell_pair(quantum_engine)

    # Entangle the bit with qubit_one
    print('Sending bit: ',bit)
    classical_encoded_message = create_message(quantum_engine=quantum_engine,qubit_one=qubit_one, message_value = bit)
    print('Encoded in classical message: ', classical_encoded_message)

    # Sending the message along with the second qubit for state re-creation
    recieved_bit = message_reciever(quantum_engine, classical_encoded_message,qubit_two)

    print('Received bit: ', recieved_bit)

def create_bell_pair(quantum_engine):
    # Qubit one is 'our' qubit, and will be used to create a message
    qubit_one = quantum_engine.allocate_qubit()
    # Qubit two is 'the receivers' qubit, and will be used to re-create the message state
    qubit_two = quantum_engine.allocate_qubit()
    '''
    Hadamard gate to put Qubit one in superposition
    This sets the value of a equal probability of being 1 or 0
    '''
    H | qubit_one

    '''
    CNOT gate to flip the second Qubit conditionally
    on the first qubit being in the state |1⟩
    '''
    CNOT | (qubit_one, qubit_two)

    return qubit_one, qubit_two


def create_message(quantum_engine='',qubit_one='', message_value = 0):

    qubit_to_send = quantum_engine.allocate_qubit()
    if message_value == 1:
        '''
        setting the qubit to positive if message_value is 1
        by flipping the base state with a Pauli-X gate.
        '''
        X | qubit_to_send


    # entangle the original qubit with the message qubit
    CNOT | (qubit_to_send, qubit_one)

    '''
    1 - Put the message qubit in superposition
    2 - Measure out the two values to get the classical bit value
        by collapsing the state.
    '''
    H | qubit_to_send
    Measure | qubit_to_send
    Measure | qubit_one

    # The qubits are now turned into normal bits we can send through classical channels
    classical_encoded_message = [int(qubit_to_send), int(qubit_one)]

    return classical_encoded_message


def message_reciever(quantum_engine,message,qubit_two):
    '''
    Pauli-X and/or Pauli-Z gates are applied to the Qubit,
    conditionally on the values in the message.
    '''
    if message[1] == 1:
        X | qubit_two
    if message[0] == 1:
        Z | qubit_two

    '''
    Measuring the Qubit and collapsing the state down to either 1 or 0
    '''
    Measure | qubit_two

    quantum_engine.flush()

    recieved_bit = int(qubit_two)
    return recieved_bit

if __name__ == "__main__":
    main()
