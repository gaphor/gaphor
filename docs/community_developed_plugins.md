## Community Developed Plugins

### Gaphor Tools Plugins

```{list-table} 
:header-rows: 1

* - Name
  - What does it do?
* - **Notes Plugin**
  - The Export Notes plugin can be used to export notes  into an Excel file, CSV file or confluence page. 
    Similarly the import plugin can be used to import any changes back to the model
* - **Export/Import Requirements Plugin**
  - The export Plugin can be used to export the requirement matrix from your gaphor model into an Excel file, csv file or to a Confluence page.
    The import Plugin on the other hand, can be used to import requirements from an Excel file, CSV file or Confluence page into the model. 
* - **Export RFIs**
  - This plugin exports all RFIs from the model into an Excel or CSV file. 
    Any comment with a name starting with `RFI` will automatically be detected and included in the export.
* - **Import Responses**
  - After RFIs have been exported and responses have been added to the Excel or CSV file, this plugin can import those responses back into the model automatically.
* - **Compare Notes / Requirements**
  - This plugin compares the Notes/Requirements currently in the model with previously exported versions to identify any differences or changes. This is especially useful when    changes may have been made to the model but have not yet been exported or reviewed.
* - **Authenticate Confluence**
  - To support importing from and exporting to Confluence, authentication is required. 
    This plugin manages the authentication session so users do not need to repeatedly authenticate during the same session.
* - **Apply Stylesheet**
  - This plugin applies a custom CSS stylesheet to the generated output, allowing formatting and styling to align with company standards or documentation guidelines.
* - **Export SDD**
  - This plugin is used to export a system Design Document (The document will only export customer facing diagrams which will have some description). 
    There are few steps on how to use this plugin
    - Using Gaphor's inbuilt plugin (Export all images to SVG/PNG), export all the diagrams
    - Run SDD plugin and save your .adoc file in the same directory as exported images
    - Then you will be asked to Run asciidoctor-pdf that will convert this .adoc file into pdf

```

#### Where can I get the above plugins?
From this [BitBucket Repo](https://bitbucket.org/resonatesystems/gaphor_tools_community/src/public-release/)
