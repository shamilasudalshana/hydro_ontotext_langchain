import re

def update_graphdb_docker_files(data_files, ontology_file):
    # Update graphdb_create.sh
    with open("graphdb_create.sh", "r") as file:
        graphdb_create_content = file.readlines()
    
    # Identify where the loadData function starts and ends
    load_data_start = next((i for i, line in enumerate(graphdb_create_content) if "function loadData" in line), None)
    load_data_end = next((i for i in range(load_data_start, len(graphdb_create_content)) if "}" in graphdb_create_content[i]), None)

    if load_data_start is not None and load_data_end is not None:
        # Replace the content between loadData function with new files
        new_data_lines = [f"    loadFile {file.name}\n" for file in data_files]
        graphdb_create_content = graphdb_create_content[:load_data_start+1] + new_data_lines + graphdb_create_content[load_data_end:]
    
    # Write the updated content back to graphdb_create.sh
    with open("graphdb_create.sh", "w") as file:
        file.writelines(graphdb_create_content)

    # Update Dockerfile
    with open("Dockerfile", "r") as file:
        dockerfile_content = file.readlines()
    
    # Find where data file COPY commands are and replace them
    copy_start = next((i for i, line in enumerate(dockerfile_content) if "COPY config.ttl" in line), None)
    copy_end = next((i for i in range(copy_start, len(dockerfile_content)) if "COPY graphdb_create.sh" in line), None)

    if copy_start is not None and copy_end is not None:
        # Prepare new COPY commands
        new_copy_lines = [f"COPY {file.name} /opt/graphdb/dist/data/repositories/langchain/\n" for file in data_files]
        dockerfile_content = dockerfile_content[:copy_start+1] + new_copy_lines + dockerfile_content[copy_end:]
    
    # Write the updated content back to Dockerfile
    with open("Dockerfile", "w") as file:
        file.writelines(dockerfile_content)

    print("Files updated successfully.")

    if __name__ == "__main__":
        a= update_graphdb_docker_files("test_file_1", "test_file_2")



