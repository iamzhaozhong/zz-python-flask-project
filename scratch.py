import wbgapi as wb

wb_gdp = wb.data.fetch('NY.GNP.PCAP.CD', time = 2020)

for row in wb_gdp:
    print(row)