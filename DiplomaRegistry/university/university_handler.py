import json
import os
from dotenv import load_dotenv
from web3 import Web3
import time
import csv
from datetime import datetime
from DiplomaRegistry.university.createPdf import generate_diploma_by_id
from eth_account.messages import encode_defunct

class DiplomaRegistryHandler:
    def __init__(self, provider_url, contract_address, abi_path, university_account, private_key):
        self.w3 = Web3(Web3.HTTPProvider(provider_url))
        with open(abi_path) as f:
            abi = json.load(f)
        self.contract = self.w3.eth.contract(address=contract_address, abi=abi)
        self.university_account = university_account
        self.private_key = private_key

    def keccak256_hash(self, data: bytes) -> bytes:
        return self.w3.keccak(data)

    def hash_file(self, file_path):
        with open(file_path, 'rb') as f:
            return self.w3.keccak(f.read())

    def sign_hash(self, hash_bytes):
        message = encode_defunct(hash_bytes)
        signed = self.w3.eth.account.sign_message(message, private_key=self.private_key)
        return signed.signature

    def get_student_id_by_cc(self, cc):
        with open('students.csv', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['cc'] == cc:
                    return row.get('student_id') or row.get('id')
        return None

    def is_eligible(self, cc):
        with open('students.csv', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['cc'] == cc:
                    date_final = datetime.strptime(row['date_final'], '%Y-%m-%d').date()
                    return date_final <= datetime.today().date()
        return False

    def mark_eligible(self, cc):
        print(f"➡️ Marking student {cc} as eligible...")
        tx = self.contract.functions.markEligible(cc).build_transaction({
            'from': self.university_account,
            'nonce': self.w3.eth.get_transaction_count(self.university_account),
            'gas': 3000000,
            'gasPrice': self.w3.to_wei('20', 'gwei')
        })
        signed_tx = self.w3.eth.account.sign_transaction(tx, private_key=self.private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print(f"⏳ Waiting for tx confirmation...")
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"✅ Marked eligible in tx: {receipt['transactionHash'].hex()}")

    def issue_diploma_for_cc(self, cc, pdf_path):
        print(f"🎓 Issuing diploma for student CC: {cc}")
        cc_hash = self.keccak256_hash(cc.encode('utf-8'))
        diploma_hash = self.hash_file(pdf_path)
        cc_signature = self.sign_hash(cc_hash)
        diploma_signature = self.sign_hash(diploma_hash)

        print(f"🔑 CC Hash: {cc_hash.hex()}")
        print(f"🖋️ Signed CC Hash (signature): {cc_signature.hex()}")
        print(f"📄 Diploma Hash: {diploma_hash.hex()}")
        print(f"🖋️ Signed Diploma Hash (signature): {diploma_signature.hex()}")

        tx = self.contract.functions.issueDiploma(
            diploma_signature,
            cc_signature
        ).build_transaction({
            'from': self.university_account,
            'nonce': self.w3.eth.get_transaction_count(self.university_account),
            'gas': 3000000,
            'gasPrice': self.w3.to_wei('20', 'gwei')
        })

        signed_tx = self.w3.eth.account.sign_transaction(tx, private_key=self.private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print(f"⏳ Issuing diploma transaction sent: {tx_hash.hex()}")
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"✅ Diploma issued in tx: {receipt['transactionHash'].hex()}")

    def listen_to_events(self):
        print("📡 Listening for events...")

        submitted_filter = self.contract.events.StudentSubmittedCC.create_filter(
            from_block=self.w3.eth.block_number,
            to_block='latest'
        )
        ineligible_filter = self.contract.events.StudentMarkedIneligible.create_filter(
            from_block=self.w3.eth.block_number,
            to_block='latest'
        )
        eligible_filter = self.contract.events.StudentMarkedEligible.create_filter(
            from_block=self.w3.eth.block_number,
            to_block='latest'
        )
        issued_filter = self.contract.events.DiplomaIssued.create_filter(
            from_block=self.w3.eth.block_number,
            to_block='latest'
        )
        paiddiploma_filter = self.contract.events.StudentPaidForDiploma.create_filter(
            from_block=self.w3.eth.block_number,
            to_block='latest'
        )

        while True:
            for event in submitted_filter.get_new_entries():
                cc = event.args['cc']
                print(f"📝 New CC submitted: {cc}")

                if self.is_eligible(cc):
                    self.mark_eligible(cc)
                else:
                    print(f"❌ Student {cc} is not eligible yet.")

            for event in eligible_filter.get_new_entries():
                cc = event.args['cc']
                print(f"✅ Student marked eligible: {cc}")

            for event in ineligible_filter.get_new_entries():
                cc = event.args['cc']
                print(f"❌ Student marked ineligible: {cc}")

            for event in issued_filter.get_new_entries():
                print(f"🎓 Diploma issued for: CC Sig = {event.args['ccSig'].hex()}")

            for event in paiddiploma_filter.get_new_entries():
                cc = event.args['cc']
                print(f"💰 Payment received from student CC: {cc}")

                student_id = self.get_student_id_by_cc(cc)
                if not student_id:
                    print(f"❌ No student ID found for CC {cc}")
                    continue

                try:
                    student_id = int(student_id)  # Convert to int to avoid type mismatch
                except ValueError:
                    print(f"❌ Invalid student ID format for CC {cc}: {student_id}")
                    continue

                pdf_path = generate_diploma_by_id(student_id)
                if not pdf_path:
                    print(f"❌ Failed to generate diploma PDF for student ID {student_id}")
                    continue

                self.issue_diploma_for_cc(cc, pdf_path)

            time.sleep(2)


if __name__ == "__main__":
    provider_url = "http://172.20.128.1:7545"
    contract_address = "0x2A3aC40C8636eA29e9C4398Beb922d61bf4ABbE3"
    abi_path = "../contract_abi.json"
    university_account = Web3(Web3.HTTPProvider(provider_url)).eth.accounts[0]
    load_dotenv()
    private_key = os.getenv("PRIVATE_KEY")
    print(f"Private Key: {private_key}")
    if not private_key:
        raise ValueError("PRIVATE_KEY not found in environment")

    handler = DiplomaRegistryHandler(provider_url, contract_address, abi_path, university_account, private_key)
    handler.listen_to_events()

