var renewables = ["Geothermal", "Hydroelectric", "Tide and Waves", "Solar", "Wind"];

var nonrenewables = ["Chemical", "Combustion", "Nuclear", "Other Production"];

var all = ["Agriculture", "Chemical", "Combustion", "Consumption Imbalance", "Other Consumption", "Total Consumption", "electricity", "Energy Industry", "Exports", "Geothermal", "Households", "Hydroelectric", "Imports", "Lost", "Lost or Stored", "Non-Energy Industries", "Nuclear", "Tide and Waves", "Production Imbalance", "Other Production", "Total Production", "Services", "Solar", "Stored", "tot_consumption", "tot_production", "Transportation", "Wind"];

var consumption = ["Agriculture", "Consumption Imbalance", "Other Consumption", "Total Consumption", "Energy Industry", "Exports", "Households", "Lost", "Lost or Stored", "Non-Energy Industries", "Services", "Stored", "tot_production", "Transportation"];

var production = ["Chemical", "Combustion", "Geothermal", "Hydroelectric", "Imports", "Nuclear", "Tide and Waves", "Production Imbalance", "Other Production", "Total Production", "Solar", "tot_consumption", "Wind"];

var exports = ["Exports"];

var imports = ["Imports"];

var import_export = ["Exports", "Imports"];

var descriptions = {
  "Agriculture": "Electricity - Consumption in agriculture, forestry and fishing",
  "chem_auto_add": "From Chemical heat -  Autoproducer",
  "chem_main_add": "From Chemical heat -  Main activity",
  "comb_auto_add": "From combustible fuels -  Autoproducer",
  "comb_main_add": "From combustible fuels -  Main activity",
  "Other Consumption": "Electricity - Consumption not elsewhere specified (other)",
  "electricity": "Electricity - Total",
  "Exports": "Electricity - exports",
  "Geothermal": "Electricity - total geothermal production",
  "Households": "Electricity - Consumption by households",
  "Hydroelectric": "Electricity - total Hydroelectric production",
  "Imports": "Electricity - imports",
  "Lost": "Electricity - Losses",
  "Non-Energy Industries": "Electricity - Consumption by manufacturing, construction and non-fuel industry",
  "Non-Renewable": "Electricity - Non-Renewable sources",
  "Nuclear": "Electricity - total Nuclear production",
  "Tide and Waves": "Electricity - total tide, wave production",
  "other_auto_add": "From other sources -  Autoproducer",
  "other_main_add": "From other sources -  Main activity",
  "own_use_1": "Electricity - Own use by electricity, heat and CHP plants",
  "own_use_2": "Electricity - Energy industries own use",
  "population": "Population",
  "Total Production": "Electricity - Gross production",
  "Renewable": "Electricity - renewable sources",
  "Services": "Electricity - Consumption by commercial and public Services",
  "Solar": "Electricity - total Solar production",
  "Stored": "Electricity - Own use by pump-storage plants",
  "Transportation": "Electricity - Consumption by transport",
  "Wind": "Electricity - total Wind production",
};

var regions = {
  "Africa": {
    "Eastern Africa": ["Burundi", "Comoros", "Djibouti", "Eritrea", "Ethiopia", "Kenya", "Madagascar", "Malawi", "Mauritius", "Mozambique", "Reunion", "Rwanda", "Seychelles", "Somalia", "Tanzania", "Uganda", "Zambia", "Zimbabwe"],
    "Middle Africa": ["Angola", "Cameroon", "Central African Republic", "Chad", "Congo", "Equatorial Guinea", "Gabon", "Sao Tome and Principe"],
    "Northern Africa": ["Algeria", "Egypt", "Libya", "Morocco", "Sudan", "Tunisia"],
    "Southern Africa": ["Botswana", "Lesotho", "Namibia", "South Africa", "Swaziland"],
    "Western Africa": ["Benin", "Burkina Faso", "Cabo Verde", "Cote dIvoire", "Gambia", "Ghana", "Guinea", "Guinea Bissau", "Liberia", "Mali", "Mauritania", "Niger", "Nigeria", "Senegal", "Sierra Leone", "St Helena", "Togo"],
  },
  "Americas": {
    "Caribbean": ["Anguilla", "Antigua and Barbuda", "Aruba", "Bahamas", "Barbados", "British Virgin Islands", "Cayman Islands", "Cuba", "Dominica", "Dominican Republic", "Grenada", "Guadeloupe", "Haiti", "Jamaica", "Martinique", "Montserrat", "Netherlands Antilles", "Puerto Rico", "St Kitts Nevis", "St Lucia", "St Vincent Grenadines", "Trinidad and Tobago", "Turks and Caicos Islands", "Virgin Islands"],
    "Central America": ["Belize", "Costa Rica", "El Salvador", "Guatemala", "Honduras", "Mexico", "Nicaragua", "Panama"],
    "Northern America": ["Bermuda", "Canada", "Greenland", "St Pierre Miquelon", "United States"],
    "South America": ["Argentina", "Bolivia", "Brazil", "Chile", "Colombia", "Ecuador", "Falkland Islands", "French Guiana", "Guyana", "Paraguay", "Peru", "Suriname", "Uruguay", "Venezuela"],
  },
  "Asia": {
    "Central Asia": ["Kazakhstan", "Kyrgyzstan", "Tajikistan", "Turkmenistan", "Uzbekistan"],
    "Eastern Asia": ["China", "China Hong Kong SAR", "China Macao SAR", "Japan", "Korea North", "Korea South", "Mongolia"],
    "South-Eastern Asia": ["Brunei Darussalam", "Cambodia", "Indonesia", "Lao", "Malaysia", "Myanmar", "Philippines", "Singapore", "Thailand", "Timor Leste", "Viet Nam"],
    "Southern Asia": ["Afghanistan", "Bangladesh", "Bhutan", "India", "Iran", "Maldives", "Nepal", "Pakistan", "Sri Lanka"],
    "Western Asia": ["Armenia", "Azerbaijan", "Bahrain", "Cyprus", "Georgia", "Iraq", "Israel", "Jordan", "Kuwait", "Lebanon", "Oman", "Qatar", "Saudi Arabia", "State of Palestine", "Syrian Arab Republic", "Turkey", "United Arab Emirates", "Yemen"],
  },
  "Europe": {
    "Eastern Europe": ["Belarus", "Bulgaria", "Czech Republic", "Hungary", "Poland", "Republic of Moldova", "Romania", "Russian Federation", "Slovakia", "Ukraine"],
    "Northern Europe": ["Denmark", "Estonia", "Faeroe Islands", "Finland", "Guernsey", "Iceland", "Ireland", "Isle of Man", "Jersey", "Latvia", "Lithuania", "Norway", "Sweden", "United Kingdom"],
    "Southern Europe": ["Albania", "Andorra", "Bosnia and Herzegovina", "Croatia", "Gibraltar", "Greece", "Italy", "Macedonia FYR", "Malta", "Montenegro", "Portugal", "Serbia", "Slovenia", "Spain"],
    "Western Europe": ["Austria", "Belgium", "France", "Germany", "Liechtenstein", "Luxembourg", "Netherlands", "Switzerland"],
  },
  "Oceania": {
    "Australia and New Zealand": ["Australia", "New Zealand"],
    "Melanesia": ["Fiji", "New Caledonia", "Papua New Guinea", "Solomon Islands", "Vanuatu"],
    "Micronesia": ["Guam", "Kiribati", "Marshall Islands", "Micronesia", "Nauru", "Northern Mariana Islands", "Palau"],
    "Polynesia": ["American Samoa", "Cook Islands", "French Polynesia", "Niue", "Samoa", "Tonga", "Tuvalu", "Wallis and Futuna Islands"],
  },
};

