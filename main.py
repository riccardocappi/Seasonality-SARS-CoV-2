import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

nations = ["Argentina",
"Australia",
"Brazil",
"Canada",
"France",
"Germany",
"Japan",
"India",
"Indonesia",
"Italy",
"Mexico",
"Russia",
"South Africa",
"Saudi Arabia",
"South Korea",
"Turkey",
"United Kingdom",
"United States",
"Spain",
"Sweden",
"Croatia",
"Hungary",
"Belgium",
"Portugal",
"Norway",
"Colombia",
"Chile",
"Denmark",
"Austria",
"Morocco"]
nations.sort()
# Carico i dati presi da https://ourworldindata.org/covid-cases aggiornati al 2021-12-24
dati = pd.read_csv("./owid-covid-data.csv")
all_distance = []
peaks_dict = {}
for nat in nations:
    peaks_dict[nat] = []

def convert_df(data, x, y, nation):
    df = data[data["location"] == nation]
    df = [df[x], df[y]]
    headers = ["x", "y"]
    filtered_data = pd.concat(df, axis=1, keys=headers)
    filtered_data.x = pd.to_datetime(filtered_data.x)
    filtered_data = filtered_data.sort_values("x")
    # Sostituisco i dati di tipo NaN con il valore 0.0
    filtered_data["y"] = filtered_data["y"].fillna(0.0)
    filtered_data["y"] = filtered_data["y"].rolling(7).mean()
    filtered_data["y"] = filtered_data["y"].fillna(0.0)
    return filtered_data

def check_real_peak(wave_period, candidate_peak):
    for n in wave_period:
        if n > candidate_peak:
            return False
    return True


def find_peaks(df,nat):
    relevant_peaks = []
    check_length = 28
    y = df["y"].values
    length = len(y)
    i = 1
    while i < length-1:
        if (y[i] >= y[i-1]) and (y[i] > y[i+1]) and (i >= check_length) and (i+check_length < length):
            if check_real_peak(np.concatenate([y[i-check_length:i],y[i+1: i+check_length+1]]), y[i]):
                threshold = np.mean(y[:i]) * 84 / 100
                if y[i] > threshold:
                    relevant_peaks.append( (i,y[i]) )
                    peaks_dict[nat].append(df['x'].values[i])
                i += check_length
        i += 1
    return relevant_peaks


def output(first_peak, second_peak):
    distance = second_peak - first_peak
    second_peak = second_peak.strftime("%Y/%m/%d")
    first_peak = first_peak.strftime("%Y/%m/%d")
    n_days = distance.days
    all_distance.append(n_days)
    print("Primo picco : " + str(first_peak), "\t", "Secondo picco: " + str(second_peak), "\t", "Distanza in giorni: " + str(n_days))

def find_max(list_of_peaks):
    first_max = 0
    second_max = 0
    index_1 = 0
    index_2 = 0
    for peak in list_of_peaks:
        if peak[1] >= first_max:
            second_max = first_max
            index_2 = index_1
            first_max = peak[1]
            index_1 = peak[0]
        elif second_max<peak[1]<first_max:
            second_max = peak[1]
            index_2 = peak[0]
    res = [index_1,index_2]
    res.sort()
    return res

for nat in nations:
    df = convert_df(dati, "date", "new_cases", nat)
    df = df.reset_index(drop=True)
    print(nat, ":")
    peaks = find_peaks(df,nat)
    print('Number of peaks','->',len(peaks))
    indexes = []
    if len(peaks) >= 2:
        indexes = find_max(peaks)
        first_peak_date = df["x"][indexes[0]]
        second_peak_date = df["x"][indexes[1]]
        output(first_peak_date,second_peak_date)

    print(np.datetime_as_string(peaks_dict[nat], unit='D'))
    print()

    df.x = df.x.dt.strftime("%Y/%m/%d")
    df.plot(
        y="y",
        x="x",
        title=nat,
        style= ".-",
        xlabel="Date",
        ylabel="New Cases"
    )

    for index in indexes:
        plt.axvline(x = index, color = "red", linewidth = 1.15)

    plt.legend(["New Cases","Peak"])
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

print("Media delle distanze tra i due picchi massimi di tutte le nazioni: " , np.mean(all_distance))
print("Varianza delle distanze tra i due picchi massimi di tutte le nazioni: " , np.var(all_distance))
print("SD delle distanze tra i due picchi massimi di tutte le nazioni: " , np.std(all_distance))

