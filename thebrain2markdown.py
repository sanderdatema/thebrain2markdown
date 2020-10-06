import json
import codecs
import html2markdown
import io

thoughts_path = "./export/thoughts.json"
links_path = "./export/links.json"
attachments_path = "./export/attachments.json"

# Relations
NOVALUE = 0
CHILD = 1
PARENT = 2
JUMP = 3
SIBLING = 4

# Attachments
INTERNALFILE = 1
EXTERNALFILE = 2
EXTERNALURL = 3
NOTESV9 = 4
ICON = 5
NOTESASSET = 6
INTERNALDIRECTORY = 7
EXTERNALDIRECTORY = 8
SUBFILE = 9
SUBDIRECTORY = 10
SAVEDREPORT = 11
MARKDOWNIMAGE = 12

links_json = {}
for line in codecs.open(links_path, "r", "utf-8-sig"):
    link = json.loads(line)
    node_id = link["ThoughtIdA"]
    if link["Meaning"] != 0:
        try:
            test = links_json[node_id]
        except KeyError:
            links_json[node_id] = []

        item = {}
        item["Link"] = link["ThoughtIdB"]
        item["Relation"] = link["Relation"]

        links_json[node_id].append(item)

# print(links_json)

attachments_json = {}
for line in codecs.open(attachments_path, "r", "utf-8-sig"):
    attachment = json.loads(line)
    node_id = attachment["SourceId"]
    try:
        test = attachments_json[node_id]
    except KeyError:
        attachments_json[node_id] = []

    item = {}
    item["Location"] = attachment["Location"]
    item["Type"] = attachment["Type"]

    attachments_json[node_id].append(item)

nodes_json = {}
for line in codecs.open(thoughts_path, "r", "utf-8-sig"):
    node = json.loads(line)
    node_id = node["Id"]
    nodes_json[node_id] = {}
    nodes_json[node_id]["Name"] = node.get("Name")
    nodes_json[node_id]["CreationDateTime"] = node.get("CreationDateTime")
    nodes_json[node_id]["Kind"] = node.get("Kind")

for key, value in nodes_json.items():
    node_id = key
    try:
        for link in links_json[node_id]:
            if link["Relation"] == CHILD:
                try:
                    nodes_json[node_id]["Children"].append(nodes_json[link["Link"]]["Name"])
                except KeyError:
                    nodes_json[node_id]["Children"] = []
                    nodes_json[node_id]["Children"].append(nodes_json[link["Link"]]["Name"])

                try:
                    nodes_json[link["Link"]]["Parents"].append(nodes_json[node_id]["Name"])
                except KeyError:
                    nodes_json[link["Link"]]["Parents"] = []
                    nodes_json[link["Link"]]["Parents"].append(nodes_json[node_id]["Name"])
            if link["Relation"] == JUMP:
                try:
                    nodes_json[node_id]["Jumps"].append(nodes_json[link["Link"]]["Name"])
                except KeyError:
                    nodes_json[node_id]["Jumps"] = []
                    nodes_json[node_id]["Jumps"].append(nodes_json[link["Link"]]["Name"])
            if link["Relation"] == SIBLING:
                try:
                    nodes_json[node_id]["Siblings"].append(nodes_json[link["Link"]]["Name"])
                except KeyError:
                    nodes_json[node_id]["Siblings"] = []
                    nodes_json[node_id]["Siblings"].append(nodes_json[link["Link"]]["Name"])
    except KeyError:
        pass

    try:
        for attachment in attachments_json[node_id]:
            if attachment["Type"] == INTERNALFILE:
                internal_file = "./export/" + node_id + "/" + attachment["Location"]
                text = []
                try:
                    for line in io.open(internal_file):
                        text.append(line)
                except UnicodeDecodeError:
                    text = ""

                text = "".join(text)
                text = html2markdown.convert(text)

                try:
                    nodes_json[node_id]["InternalFile"].append(text)
                except KeyError:
                    nodes_json[node_id]["InternalFile"] = []
                    nodes_json[node_id]["InternalFile"].append(text)

            if attachment["Type"] == NOTESV9:
                notesv9 = "./export/" + node_id + "/Notes/" + attachment["Location"]
                text = []
                for line in io.open(notesv9):
                    text.append(line)

                text = "".join(text)
                text = html2markdown.convert(text)

                try:
                    nodes_json[node_id]["Notes"].append(text)
                except KeyError:
                    nodes_json[node_id]["Notes"] = []
                    nodes_json[node_id]["Notes"].append(text)

            if attachment["Type"] == EXTERNALFILE:
                try:
                    nodes_json[node_id]["ExternalFile"].append(attachment["Location"])
                except KeyError:
                    nodes_json[node_id]["ExternalFile"] = []
                    nodes_json[node_id]["ExternalFile"].append(attachment["Location"])
            if attachment["Type"] == EXTERNALURL:
                try:
                    nodes_json[node_id]["ExternalURL"].append(attachment["Location"])
                except KeyError:
                    nodes_json[node_id]["ExternalURL"] = []
                    nodes_json[node_id]["ExternalURL"].append(attachment["Location"])
            if attachment["Type"] == NOTESASSET or attachment["Type"] == MARKDOWNIMAGE:
                try:
                    nodes_json[node_id]["Image"].append(attachment["Location"])
                except KeyError:
                    nodes_json[node_id]["Image"] = []
                    nodes_json[node_id]["Image"].append(attachment["Location"])
    except KeyError:
        pass


for _, value in nodes_json.items():
    contents = []
    name = value["Name"].replace("/", "-")
    filename = "./obsidian/" + name + ".md"
    text_file = open(filename, "w")
    if "InternalFile" in value:
        for attachment in value["InternalFile"]:
            attachment = attachment.replace(":{", "")
            attachment = attachment.replace(":}", "")
            text_file.write("\n" + attachment)
    if "Notes" in value:
        for attachment in value["Notes"]:
            attachment = attachment.replace(":{", "")
            attachment = attachment.replace(":}", "")
            text_file.write("\n" + attachment)
    if "ExternalFile" in value:
        for attachment in value["ExternalFile"]:
            text_file.write("\nAttachment: [[" + attachment + "]]")
    if "ExternalURL" in value:
        for attachment in value["ExternalURL"]:
            text_file.write("\nExternal URL: " + attachment)
    if "Image" in value:
        for attachment in value["Image"]:
            text_file.write("\n![[" + attachment + "]]")
    if "Children" in value or "Parents" in value or "Jumps" in value:
        text_file.write("\n\n")
    if "Children" in value:
        text_file.write("\nChildren: ")
        text = ", ".join([str("[[" + item + "]]") for item in value["Children"]])
        text = text.replace("/", "-")
        text_file.write(text)
    if "Parents" in value:
        text_file.write("\nParents: ")
        text = ", ".join([str("[[" + item + "]]") for item in value["Parents"]])
        text = text.replace("/", "-")
        text_file.write(text)
    if "Jumps" in value:
        text_file.write("\nJumps: ")
        text = ", ".join([str("[[" + item + "]]") for item in value["Jumps"]])
        text = text.replace("/", "-")
        text_file.write(text)

    text_file.close()
