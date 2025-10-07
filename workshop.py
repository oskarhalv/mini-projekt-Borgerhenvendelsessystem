import csv
import os

# --- Klasser ---
class Person:
    def __init__(self, navn, CPR, køn):
        self.navn = navn
        self.CPR = CPR
        self.køn = køn

    def __str__(self):
        return f"Navn: {self.navn}, CPR: {self.CPR}, Køn: {self.køn}"

    @property
    def CPR(self) -> int:
        return self._CPR

    @CPR.setter
    def CPR(self, value):
        try:
            value = int(value)
        except (TypeError, ValueError):
            raise TypeError("CPR skal være et heltal; decimaltal afrundes") from None
        if value < 0:
            raise ValueError("CPR kan ikke være negativ")
        self._CPR = value
        
class Elev(Person):
    def __init__(self, navn, CPR, køn, Region, Kommune):
        super().__init__(navn, CPR, køn)
        self.Region = Region
        self.Kommune = Kommune

    def __str__(self):
        return f"{super().__str__()}, Region: {self.Region}, Kommune: {self.Kommune}"


class Lærer(Person):
    """
    Lærer-klasse der udvider Person med email, telefon og fag.
    Demonstrerer properties med validering for at beskytte data-integritet.
    """
    def __init__(self, navn, alder, køn, email, telefon, fag=None):
        super().__init__(navn, alder, køn)
        # Brug properties - dette kalder automatisk setters med validering
        self.email = email
        self.telefon = telefon
        self._fag = fag if fag else []
    
    @property
    def email(self):
        """
        Getter for email - returnerer den interne værdi.
        """
        return self._email
    
    @email.setter
    def email(self, value):
        """
        Setter for email med validering.
        Sikrer at emailen har et gyldigt format (noget@noget.noget).
        """
        if not isinstance(value, str):
            raise TypeError("Email skal være tekst")
        
        # Regex mønster for email-validering
        email_mønster = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_mønster, value):
            raise ValueError("Email skal have formatet: navn@domæne.dk")
        
        self._email = value
    
    @property
    def telefon(self):
        """Getter for telefon - returnerer formateret telefonnummer."""
        return self._telefon
    
    @telefon.setter
    def telefon(self, value):
        """
        Setter for telefon med validering og formatering.
        Accepterer forskellige input-formater men standardiserer til ét format.
        """
        # Fjern mellemrum og bindestreger for at standardisere
        renset = value.replace(" ", "").replace("-", "")
        
        # Validér at det kun er tal
        if not renset.isdigit():
            raise ValueError("Telefonnummer må kun indeholde tal")
        
        # Validér længde (dansk telefonnummer = 8 cifre)
        if len(renset) != 8:
            raise ValueError("Dansk telefonnummer skal være 8 cifre")
        
        # Gem i standardformat for læsbarhed: XX XX XX XX
        self._telefon = f"{renset[:2]} {renset[2:4]} {renset[4:6]} {renset[6:]}"
    

# --- Filnavn ---
FILENAME = "personliste.csv"


# --- Gem listen til CSV ---
def gem_personer_csv(personer):
    # Find mappen hvor .py filen ligger
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Kombiner med filnavnet
    filepath = os.path.join(script_dir, FILENAME)
    
    felt_navn = ["navn", "CPR", "køn", "Region", "Kommune"]
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=felt_navn)
        writer.writeheader()
        for p in personer:
            row = {
                "navn": p.navn,
                "CPR": p.CPR,
                "køn": p.køn,
                "Region": getattr(p, "Region", ""),
                "Kommune": getattr(p, "Kommune", "")
            }
            writer.writerow(row)
    print(f"Listen er gemt i '{filepath}' (CSV-fil).")


# --- Indlæs liste fra CSV ---
def indlaes_personer_csv():
    # Find mappen hvor .py filen ligger
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Kombiner med filnavnet
    filepath = os.path.join(script_dir, FILENAME)
    
    personer = []
    if os.path.exists(filepath):
        with open(filepath, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                navn = row["navn"]
                CPR = int(row["CPR"])
                køn = row["køn"]
                Region = row.get("Region", "")
                Kommune = row.get("Kommune", "")
                if Region or Kommune:
                    personer.append(Elev(navn, CPR, køn, Region, Kommune))
                else:
                    personer.append(Person(navn, CPR, køn))
        print(f"{len(personer)} personer/elev indlæst fra '{filepath}'")
    else:
        print("Ingen tidligere fil fundet, starter med tom liste.")
    return personer


# --- Terminalprogram ---
def main():
    personer = indlaes_personer_csv()  # indlæs eksisterende CSV

    while True:
        print("\n--- Person/Elev Registrering ---")
        print("1. Tilføj person")
        print("2. Vis alle personer")
        print("3. Tilføj person til Region")
        print("4. Gem liste som CSV")
        print("5. Afslut")
        valg = input("Vælg en mulighed: ")

        if valg == "1":
            navn = input("Indtast navn: ")
            CPR = input("Indtast CPR: ")
            køn = input("Indtast køn: ")
            try:
                CPR = int(CPR)
                p = Person(navn, CPR, køn)
                personer.append(p)
                print("Person tilføjet!")
            except ValueError:
                print("⚠ CPR skal være et heltal.")

        elif valg == "2":
            if not personer:
                print("Ingen personer registreret endnu.")
            else:
                print("\n--- Registrerede personer/elev ---")
                for i, person in enumerate(personer, start=1):
                    print(f"{i}. {person}")

        elif valg == "3":
            ikke_elever = [p for p in personer if not isinstance(p, Elev)]
            if not ikke_elever:
                print("Ingen personer at opgradere.")
                continue

            print("\nVælg en person at opgradere til elev:")
            for i, person in enumerate(ikke_elever, start=1):
                print(f"{i}. {person}")

            try:
                valg_index = int(input("Nummer: ")) - 1
                person_valgt = ikke_elever[valg_index]
            except (ValueError, IndexError):
                print("Ugyldigt valg.")
                continue

            Region = input("Indtast Region: ")
            Kommune = input("Indtast Kommune: ")
            elev = Elev(person_valgt.navn, person_valgt.CPR, person_valgt.køn, Region, Kommune)
            personer[personer.index(person_valgt)] = elev
            print(f"{elev.navn} er nu elev på {Region}, Kommune {Kommune}!")

        elif valg == "4":
            gem_personer_csv(personer)

        elif valg == "5":
            print("Program afsluttes.")
            gem_personer_csv(personer)
            break

        else:
            print("Ugyldigt valg, prøv igen.")


if __name__ == "__main__":
    main()