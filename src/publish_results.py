import csv
from typing import List, Dict

# This function is for publishing the results to the website in a table.
from src.reflections_judges_platform import rename_dict_keys, make_url
from src.utils import split_csv


def decorate_url(url, file_type, title):
    if file_type in ["mp3", "mp4", "pdf", "docx", "doc"]:
        return f'<iframe src="{url}" height ="100%" width="100%"></iframe>'
    elif file_type in ["jpg", "jpeg", "png"]:
        return f'<img alt="{title}" src="{url}" height ="100%" width="100%">'


def mk_school(school_dict_entry):
    school_prefix = school_dict_entry
    school_suffix = "Elementary school" if not school_prefix.endswith("High") and not school_prefix.endswith("Middle") else "school"
    return f"{school_prefix} {school_suffix}"


def publish_results(selected_ids: List[str], honorable_ids: List[str], in_fp, out_fp, out_fp_table):
    with open(out_fp, 'w') as o_handle:
        o_handle.write("""
        <!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<style>

table {
  border-collapse: collapse;
  width: 80%;
}

th, td {
  padding: 8px;
  text-align: left;
  border-bottom: 1px solid #DDD;
}

tr:hover {background-color: lightyellow}


div.gallery {
  margin: 5px;
  border: 1px solid #ccc;
  float: left;
  width: 180px;
}

div.gallery:hover {
  border: 1px solid #777;
}

table td, table td * {
    vertical-align: top;
}

div.gallery img {
  width: 100%;
  height: auto;
}

div.desc {
  padding: 15px;
  text-align: center;
}
</style>
</head>
<body>
<h3>District 🏆finalists🏆 advancing to state [<a target="_blank" href="finalists.html">see list here</a>]. Also, listed here are the honorable mentions 🎖</h3>
""") # </body> </html>

        categorized_data: Dict[str, List[Dict]] = {}
        with open(in_fp) as f_handle:
            for d in csv.DictReader(f_handle):
                rename_dict_keys(d)
                if d["entry_id"] not in selected_ids and d["entry_id"] not in honorable_ids:
                    continue
                d['trophy'] = "🏆" if d["entry_id"] in selected_ids else "🎖"

                # organize by category.
                if d['entry_category'] not in categorized_data:
                    categorized_data[d['entry_category']] = []
                categorized_data[d['entry_category']].append(d)

        categories_desired_order = ['Visual Arts', 'Music Composition', 'Dance Choreography', 'Film Production', 'Literature', 'Photography']

        # categories_sorted = sorted(list(categorized_data.keys()))
        for category in categories_desired_order:
            unsorted_data = categorized_data[category]

            # sort by first name (input= list[dicts]).
            # first all finalists and then all honorable mentions.
            data_finalists = sorted([x for x in unsorted_data if x['trophy'] == "🏆"], key=lambda item: item['entry_student_first_name'])
            data_honorable = sorted([x for x in unsorted_data if x['trophy'] == "🎖"], key=lambda item: item['entry_student_first_name'])

            o_handle.write(f"""\n<br><br><div style="border: 2px outset black;
  background-color: lightyellow;    
  text-align: left; width: 80%" ><h3>Category: {category}</h3></div>\n<table style="vertical-align: bottom;">""")
            td_cnt = 0
            td_max = 5


            for data in [data_finalists, data_honorable]:
                for d in data:
                    if td_cnt % td_max == 0:
                        o_handle.write("<tr>")

                    # <div class="gallery">
                    #    <iframe src="https://drive.google.com/file/d/1YMXwBVTuxsgNChpWqG-dBeP9EJYl_XjI/preview" height ="100%" width="100%"></iframe>
                    # OR <img src="img_forest.jpg" alt="Forest" width="100%" height="100%">
                    #    <div class="desc">Add a description of the image here <a target="_blank" style="text-decoration:none;" href=https://drive.google.com/file/d/1YMXwBVTuxsgNChpWqG-dBeP9EJYl_XjI/preview>↗</a></div>
                    # </div>

                    # Only display the first image/ file.
                    first_url = split_csv(d['entry_urls'])[0]
                    first_file_type = split_csv(d['entry_file_types'])[0]
                    mk_url = make_url(file_type=first_file_type, url=first_url)
                    decorated_mk_url = decorate_url(url=mk_url, file_type=first_file_type, title=d['entry_title'])
                    # '1Ws9x6GhUIDmY75CptcsVO2WiWdgA1C7j'
                    # '1Ws9x6GhUIDmY75CptcsVO2WiWdgA1C7j'

                    desc_txt = f"{d['trophy']} {d['entry_student_first_name']} {d['entry_student_last_name']} <br>" \
                               f"<i>{d['entry_title']}</i>\n<br><br>"
                    # f"\n{d['entry_grade_division']} | {mk_school(d['School:'])}"
                    description = f'<div class="desc">{desc_txt} ' \
                                  f'</div>'
                    # f'<a target="_blank" style="text-decoration:none;" href={first_url}>↗</a>' \

                    o_handle.write("<td>")
                    o_handle.write(f"""
    <div class="gallery">
    <a target="_blank" href="{mk_url}">
    {decorated_mk_url}
    </a>
    {description}
    </div>
    """)
                    o_handle.write("</td>\n")
                    td_cnt += 1
                    if td_cnt % td_max == 0:
                        o_handle.write("</tr>\n")







            o_handle.write("</table>\n")


        with open(out_fp_table, 'w') as o_table_handle:
            o_table_handle.write(""" <html> 
            <head>
            <meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<style>

table {
  border-collapse: collapse;
  width: 80%;
}

th, td {
  padding: 8px;
  text-align: left;
  border-bottom: 1px solid #DDD;
}

tr:hover {background-color: #D6EEEE;}

#search_query {
  background-image: url('/css/searchicon.png');
  background-position: 10px 10px;
  background-repeat: no-repeat;
  width: 80%;
  font-size: 16px;
  padding: 12px 20px 12px 40px;
  border: 1px solid #ddd;
  margin-bottom: 12px;
}

div.gallery {
  margin: 5px;
  border: 1px solid #ccc;
  float: left;
  width: 180px;
}

div.gallery:hover {
  border: 1px solid #777;
}

table td, table td * {
    vertical-align: top;
}
</style>

<script>
function search_studentname_or_schoolname() {
  var input, filter, table, tr, td, i, txtValue;
  input = document.getElementById("search_query");
  filter = input.value.toUpperCase();
  table = document.getElementById("finalists");
  tr = table.getElementsByTagName("tr");
  for (i = 0; i < tr.length; i++) {
    td_studentname = tr[i].getElementsByTagName("td")[0];
    td_schoolname = tr[i].getElementsByTagName("td")[1];
    
    if (td_studentname) {
      studentValue = td_studentname.textContent || td_studentname.innerText;
      schoolValue = td_schoolname.textContent || td_schoolname.innerText;
      
      if (studentValue.toUpperCase().indexOf(filter) > -1 || schoolValue.toUpperCase().indexOf(filter) > -1 ) {
        tr[i].style.display = "";
      } else {
        tr[i].style.display = "none";
      }
    }
    
           
  }
}
</script>

</head>
            
            <body> <br>
            <h3><h3>District 🏆finalists🏆 advancing to state. <br>Also, listed here are the honorable mentions 🎖</h3><br></h3>
            <br>
            
            <input type="text" id="search_query" onkeyup="search_studentname_or_schoolname()" placeholder="Search..." title="Type in a name">

            <table id="finalists" style="border: 1px"> 
                <tr>
                    <th>Student name</th> 
                    <th>School</th>
                    <th>Grade division</th>
                    <th>Category</th>
                </tr>
                """)
            for category in categories_desired_order:
                unsorted_data = categorized_data[category]

                # sort by first name (input= list[dicts]).
                # first all finalists and then all honorable mentions.
                data_finalists = sorted([x for x in unsorted_data if x['trophy'] == "🏆"], key=lambda item: item['entry_student_first_name'])
                data_honorable = sorted([x for x in unsorted_data if x['trophy'] == "🎖"], key=lambda item: item['entry_student_first_name'])


                # <table>
                #   <tr>
                #     <th>First Name</th>
                #     <th>Last Name</th>
                #     <th>Points</th>
                #   </tr>
                #   <tr>
                #     <td>Peter</td>
                #     <td>Griffin</td>
                #     <td>$100</td>
                #   </tr>

                # two empty lines before change of category.
                # o_handle.write("<tr><td></td><td></td><td></td><td></td></tr>")
                # o_handle.write("<tr><td></td><td></td><td></td><td></td></tr>")

                for data in [data_finalists, data_honorable]:
                    # o_handle.write("<tr><td></td><td></td><td></td><td></td></tr>")
                    for d in data:
                        o_table_handle.write(f"""<tr>
                        <td>{d['trophy']} {d['entry_student_first_name']} {d['entry_student_last_name']}</td> 
                        <td>{mk_school(d['School:'])}</td>
                        <td>{d['entry_grade_division']}</td>
                        <td>{category}</td>
                        </tr>""")
            o_table_handle.write("\n</table><br><br><hr><br>")
            o_table_handle.write("</body></html>")

        o_handle.write("</body></html>")
        print(f"Saving results file to {out_fp}")


if __name__ == '__main__':
    # to publish results
    selected_ids_csv = "207, 200, 142, 150, 45, 46, 81, 104, 94, 47, 130, 199, 176, 57, 101, 138, 61, 58, 103, 125, 55, 100, 51, 119, 40, 202, 109, 71, 66, 126, 217, 143, 152, 72, 82, 148, 178, 127, 213, 175, 59, 52, 173, 201, 85, 102, 107, 203, 147, 106, 141, 129, 212, 214, special1, special2, special3"
    honorable_ids_csv = "209, 89, 25, 124, 149, 182, 137, 88, 53, 96, 208, 31, 5, 3, 111, 220, 97, 17, 93, 98"
    publish_results(selected_ids=[x.strip() for x in selected_ids_csv.split(",")],
                    honorable_ids=[x.strip() for x in honorable_ids_csv.split(",")],
                    in_fp= "data/confidential/reflections-isd-to-evaluate.csv",
                    out_fp="/tmp/results.html",
                    out_fp_table="/tmp/finalists.html"
                    )