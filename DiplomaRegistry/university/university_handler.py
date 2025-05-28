import json
import time
from web3 import Web3
from DiplomaRegistry.university.createPdf import generate_diploma_by_id
from utils import keccak256_hash, sign_hash
from student_data import get_student_id_by_cc, is_student_eligible,remove_student_by_hash,get_cc_by_hash

class DiplomaRegistryHandler:
    def __init__(self, provider_url, contract_address, abi_path, university_account, private_key):
        self.w3 = Web3(Web3.HTTPProvider(provider_url))
        with open(abi_path) as f:
            abi = json.load(f)
        self.contract = self.w3.eth.contract(address=contract_address, abi=abi)
        self.university_account = university_account
        self.private_key = private_key

    def hash_file(self, file_path):
        with open(file_path, 'rb') as f:
            return self.w3.keccak(f.read())

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

    def mark_ineligible(self, cc):
        print(f"➡️ Marking student {cc} as ineligible...")
        tx = self.contract.functions.markIneligible(cc).build_transaction({
            'from': self.university_account,
            'nonce': self.w3.eth.get_transaction_count(self.university_account),
            'gas': 3000000,
            'gasPrice': self.w3.to_wei('20', 'gwei')
        })
        signed_tx = self.w3.eth.account.sign_transaction(tx, private_key=self.private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print(f"⏳ Waiting for tx confirmation...")
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"✅ Marked ineligible in tx: {receipt['transactionHash'].hex()}")

    def issue_diploma_for_cc(self, cc, pdf_path):
        print(f"🎓 Issuing diploma for student CC: {cc}")
        cc_hash = keccak256_hash(cc.encode('utf-8'))
        diploma_hash = self.hash_file(pdf_path)
        cc_signature = sign_hash(cc_hash, self.private_key)
        diploma_signature = sign_hash(diploma_hash, self.private_key)

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
        studentremoved_filter = self.contract.events.StudentRemoved.create_filter(
            from_block=self.w3.eth.block_number,
            to_block='latest'
        )

        while True:
            for event in submitted_filter.get_new_entries():
                hashed_cc = event.args['ccHash']
                cc = get_cc_by_hash(hashed_cc)
                print(f"📝 New CC submitted: {cc}")

                if is_student_eligible(cc):
                    self.mark_eligible(hashed_cc)
                else:
                    self.mark_ineligible(hashed_cc)

            for event in studentremoved_filter.get_new_entries():
                remove_student_by_hash(event.args['ccHash'])

            for event in eligible_filter.get_new_entries():
                hashed_cc = event.args['ccHash']
                cc = get_cc_by_hash(hashed_cc)
                print(f"✅ Student marked eligible: {cc}")

            for event in ineligible_filter.get_new_entries():
                hashed_cc = event.args['ccHash']
                cc = get_cc_by_hash(hashed_cc)
                print(f"❌ Student marked ineligible: {cc}")

            for event in issued_filter.get_new_entries():
                print(f"🎓 Diploma issued for: CC Sig = {event.args['ccSig'].hex()}")

            for event in paiddiploma_filter.get_new_entries():
                hashed_cc = event.args['ccHash']
                cc = get_cc_by_hash(hashed_cc)
                print(f"💰 Payment received from student CC: {cc}")

                student_id = get_student_id_by_cc(cc)
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
