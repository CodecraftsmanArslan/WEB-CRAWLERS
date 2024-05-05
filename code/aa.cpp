#include <iostream>
#include <cstdio>
#include <cstring>
#include <cstdlib>
using namespace std;

//a) SingleNode and SingleLinkedList classes:


class SingleNode {
public:
    int data;
    SingleNode* next;
};

class SingleLinkedList {
private:
    SingleNode* head;
public:
    SingleLinkedList();
    void InsertFirst(int data);
    int RemoveFirst();
    void PrintAll();
};
//b) Constructors of both classes:


SingleLinkedList::SingleLinkedList() {
    head = NULL;
}
//c) InsertFirst( ) and RemoveFirst Functions:


void SingleLinkedList::InsertFirst(int data) {
    SingleNode* newNode = new SingleNode();
    newNode->data = data;
    newNode->next = head;
    head = newNode;
}

int SingleLinkedList::RemoveFirst() {
    if (head == NULL)
        return -1;

    SingleNode* temp = head;
    head = head->next;
    int data = temp->data;
    delete temp;
    return data;
}
//d) PrintAll( ) function:


void SingleLinkedList::PrintAll() {
    SingleNode* current = head;
    while (current != NULL) {
        cout << current->data << " ";
        current = current->next;
    }
    cout << endl;
}
//e) Main menu to demonstrate the functionality:


int main() {
    SingleLinkedList list;
    int choice, data;
    while (true) {
        cout << "1. InsertFirst" << endl;
        cout << "2. RemoveFirst" << endl;
        cout << "3. PrintAll" << endl;
        cout << "4. Quit" << endl;
        cout << "Enter your choice: ";
        cin >> choice;
        switch (choice) {
            case 1:
                cout << "Enter the data: ";
                cin >> data;
                list.InsertFirst(data);
                break;
            case 2:
                data = list.RemoveFirst();
                if (data == -1)
                    cout << "List is empty" << endl;
                else
                    cout << "Removed data: " << data << endl;
                break;
            case 3:
                cout << "List elements: ";
                list.PrintAll();
                break;
            case 4:
                return 0;
        }
    }
    return 0;
}