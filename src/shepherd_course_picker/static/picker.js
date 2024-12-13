
class Node {
    constructor(input_data, depth=0) {
        this.depth = depth
        // Empty list of children
        this.childNodes = []

        // Create a new DOM element for myself!
        this.element = document.createElement('div')

        this.element.classList.add('node');

        // For styling purposes (CSS is too hard)
        this.element.setAttribute('depth', depth);

        // Set my title
        this.element.textContent = input_data['name']

        if (input_data['text']) {
            input_data['text'].forEach(text => {
                let new_element = document.createElement('p')
                new_element.textContent = text
                this.element.appendChild(
                    new_element
                )
            })
        }

        // Recursively append children to myself
        if (input_data['nodes']) {
            input_data['nodes'].forEach(child_data => {
                let newone = new Node(
                    child_data,
                (this.depth === 1 ? 0 : 1)
                )
                this.appendChildNode(newone)
                }
            );
        }


    }

    appendChildNode(node){
        this.childNodes.push(
            node
        )
        this.element.appendChild(
            node.element
        )

        console.log("hi")
    }

}

var rootNode = null

document.addEventListener("DOMContentLoaded", () => {
    // Function to fetch data from the server
    async function fetchData() {
        try {
            // Send a GET request to the server
            const response = await fetch(`/api/programs/${2576}`);
            // if (!response.ok) {
            //     throw new Error(`HTTP error! Status: ${response.status}`);
            // }

            // Parse the JSON response
            const data = await response.json();
            // console.log(data)
            rootNode = new Node(
                data
            )
            document.getElementsByClassName("node")[0].appendChild(
                rootNode.element
            )
            console.log(rootNode)
            // processNode(
            //     data,
            //     document.getElementsByClassName("node")[0]
            // )
            // Insert data into the table
            // populateTable(data);
        } catch (error) {
            console.error("Error fetching data:", error);
        }
    }

    // Fetch data when the page loads
    fetchData();
});
