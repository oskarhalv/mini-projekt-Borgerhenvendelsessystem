import csv
import os
import re

# --- Klasser ---
class Person:
    def __init__(self, navn, CPR, køn, Region, Kommune):
        self.navn = navn
        self.CPR = CPR  # kalder property
        self.køn = køn
        self.Region = Region
        self.Kommune = Kommune

    def __str__(self):
        if self.Region or self.Kommune:
            return f"Navn: {self.navn}, CPR: {self.CPR}, Køn: {self.køn}, Region: {self.Region}, Kommune: {self.Kommune}"
        return f"Navn: {self.navn}, CPR: {self.CPR}, Køn: {self.køn}"

    @property
    def CPR(self) -> str:
        return self._CPR

    @CPR.setter
    def CPR(self, value):
        # Sørg for at CPR er en streng
        value = str(value).strip()
        clean_value = value.replace("-", "").replace(" ", "")

        # Tjek at CPR kun består af tal
        if not clean_value.isdigit():
            raise ValueError(f"CPR må kun indeholde tal og evt. en bindestreg (fik: {value})")

        # Tjek længden
        if len(clean_value) != 10:
            raise ValueError(f"CPR skal være præcis 10 cifre — du indtastede {len(clean_value)} ({value})")

        self._CPR = value


class Medarbejder(Person):
    """
    Medarbejder klassen skal bruges til at Medarbejder kan se henvendelserne 
    """
    def __init__(self, navn, CPR, køn, email, telefon, Region, Kommune):
        super().__init__(navn, CPR, køn, Region, Kommune)
        self._email = None  # Initialize before setter
        self._telefon = None  # Initialize before setter
        self.email = email
        self.telefon = telefon
        self.afdelinger = []

    def tilføj_afdeling(self, afdeling):
        if afdeling not in self.afdelinger:
            self.afdelinger.append(afdeling)
            return True
        return False

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, value):
        if not isinstance(value, str):
            raise TypeError("Email skal være tekst")
        email_mønster = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_mønster, value):
            raise ValueError("Email skal have formatet: navn@domæne.dk")
        self._email = value

    @property
    def telefon(self):
        return self._telefon

    @telefon.setter
    def telefon(self, value):
        renset = value.replace(" ", "").replace("-", "")
        if not renset.isdigit():
            raise ValueError("Telefonnummer må kun indeholde tal")
        if len(renset) != 8:
            raise ValueError("Dansk telefonnummer skal være 8 cifre")
        self._telefon = f"{renset[:2]} {renset[2:4]} {renset[4:6]} {renset[6:]}"


# --- Filnavn ---
FILENAME = "personliste.csv"


# --- Gem listen til CSV ---
def gem_personer_csv(personer):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(script_dir, FILENAME)

    felt_navn = ["navn", "CPR", "køn", "Region", "Kommune"]
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=felt_navn)
        writer.writeheader()
        for p in personer:
            writer.writerow({
                "navn": p.navn,
                "CPR": p.CPR,
                "køn": p.køn,
                "Region": getattr(p, "Region", ""),
                "Kommune": getattr(p, "Kommune", "")
            })
    print(f"✅ Listen er gemt i '{filepath}'.")


# --- Indlæs liste fra CSV ---
def indlaes_personer_csv():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(script_dir, FILENAME)

    personer = []
    if os.path.exists(filepath):
        with open(filepath, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                navn = row["navn"].strip()
                CPR = row["CPR"].strip()
                køn = row["køn"].strip()
                Region = row.get("Region", "").strip()
                Kommune = row.get("Kommune", "").strip()
                try:
                    personer.append(Person(navn, CPR, køn, Region, Kommune))
                except ValueError as e:
                    print(f"⚠ Fejl i indlæsning af '{navn}': {e}")
        print(f"📥 {len(personer)} personer indlæst fra '{filepath}'")
    else:
        print("Ingen tidligere fil fundet. Starter med tom liste.")
    return personer


# --- Terminalprogram ---
def main():
    personer = indlaes_personer_csv()

    while True:
        print("\n--- Person Registrering ---")
        print("1. Tilføj person")
        print("2. Vis alle personer")
        print("3. Tilføj Medarbejder")
        print("4. Tilføj Region/Kommune til person")
        print("5. Gem liste som CSV")
        print("6. Afslut")
        valg = input("Vælg en mulighed: ").strip()

        if valg == "1":
            navn = input("Indtast navn: ").strip()
            CPR = input("Indtast CPR (fx 010203-1234): ").strip()
            køn = input("Indtast køn: ").strip()
            Region = input("Indtast Region: ").strip()
            Kommune = input("Indtast Kommune: ").strip()

            try:
                p = Person(navn, CPR, køn, Region, Kommune)
                personer.append(p)
                print(f"✅ Person '{navn}' tilføjet!")
            except ValueError as e:
                print(f"⚠ Fejl: {e}")
    
        elif valg == "2":
            if not personer:
                print("Ingen personer registreret endnu.")
            else:
                print("\n--- Registrerede personer ---")
                for i, person in enumerate(personer, start=1):
                    print(f"{i}. {person}")

        elif valg == "3":
            print("\n--- Tilføj ny Medarbejder ---")
            navn = input("Indtast navn: ")
            CPR = input("Indtast CPR: ")
            køn = input("Indtast køn: ")
            Region = input("Indtast Region: ")
            Kommune = input("Indtast Kommune: ")
            email = input("Indtast email: ")
            telefon = input("Indtast telefon (8 cifre): ")
            
            try:
                M = Medarbejder(navn, CPR, køn, email, telefon, Region, Kommune)
                print("\nTilføj afdeling (tryk Enter uden at skrive noget for at afslutte)")
                while True:
                    afdeling = input("Afdeling: ").strip()
                    if not afdeling:
                        break
                    if M.tilføj_afdeling(afdeling):
                        print(f"  ✓ {afdeling} tilføjet")
                
                personer.append(M)
                print(f"✓ Medarbejder {navn} tilføjet!")
            except (ValueError, TypeError) as e:
                print(f"⚠ Fejl: {e}")

        elif valg == "4":
            personer_uden_region = [p for p in personer if not p.Region or not p.Kommune]
            if not personer_uden_region:
                print("Ingen personer uden Region/Kommune.")
                continue

            print("\nVælg en person at tilføje Region/Kommune til:")
            for i, person in enumerate(personer_uden_region, start=1):
                print(f"{i}. {person}")

            try:
                valg_index = int(input("Nummer: ")) - 1
                person_valgt = personer_uden_region[valg_index]
            except (ValueError, IndexError):
                print("Ugyldigt valg.")
                continue

            Region = input("Indtast Region: ").strip()
            Kommune = input("Indtast Kommune: ").strip()
            person_valgt.Region = Region
            person_valgt.Kommune = Kommune
            print(f"✅ {person_valgt.navn} har nu Region: {Region}, Kommune: {Kommune}!")

        elif valg == "5":
            gem_personer_csv(personer)

        elif valg == "6":
            print("💾 Program afsluttes. Gemmer data...")
            gem_personer_csv(personer)
            break

        else:
            print("⚠ Ugyldigt valg, prøv igen.")


if __name__ == "__main__":
    main()