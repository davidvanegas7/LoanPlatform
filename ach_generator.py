import datetime

def generate_ach_file(file_header, batch_header, entries, batch_control, file_control):
    """Generates an ACH file string from provided record data."""

    ach_string = ""
    ach_string += file_header + "\n"
    ach_string += batch_header + "\n"

    for entry in entries:
        ach_string += entry + "\n"

    ach_string += batch_control + "\n"
    ach_string += file_control

    return ach_string

def create_file_header(destination_routing, origin_routing, destination_name, origin_name):
    """Creates a File Header record."""
    record_type = "1"
    priority_code = "01"
    file_creation_date = datetime.datetime.now().strftime("%y%m%d")
    file_creation_time = datetime.datetime.now().strftime("%H%M")
    file_id_modifier = "A"
    record_size = "094"
    blocking_factor = "10"
    format_code = "1"
    destination = destination_routing.ljust(10)
    origin = origin_routing.ljust(10)
    destination_name_padded = destination_name.ljust(23)
    origin_name_padded = origin_name.ljust(23)
    reference_code = "".ljust(8)
    
    return f"{record_type}{priority_code}{destination_routing}{origin_routing}{file_creation_date}{file_creation_time}{file_id_modifier}{record_size}{blocking_factor}{format_code}{destination_name_padded}{origin_name_padded}{reference_code}"

def create_batch_header(service_class_code, company_name, company_identification, standard_entry_class_code, company_entry_description, originating_dfi_id):
  """Creates a Batch Header record."""
  record_type = "5"
  # Service Class Code: 200 (ACH credits only), 220 (ACH debits only), 225 (mixed debits and credits)
  company_name_padded = company_name.ljust(16)
  company_discretionary_data = "".ljust(20)
  company_entry_description_padded = company_entry_description.ljust(10)
  effective_entry_date = datetime.datetime.now().strftime("%y%m%d")
  settlement_date_julian = "   " 
  originating_dfi_id_padded = originating_dfi_id.ljust(8)
  batch_number = "0001" #increment for multiple batches
  
  return f"{record_type}{service_class_code}{company_name_padded}{company_discretionary_data}{company_identification}{standard_entry_class_code}{company_entry_description_padded}{effective_entry_date}{settlement_date_julian}{originating_dfi_id_padded}{batch_number}"

def create_entry_detail(transaction_code, receiving_dfi_routing_number, dda_account_number, amount, individual_id_number, individual_name, discretionary_data, addenda_record_indicator):
    """Creates an Entry Detail record."""
    record_type = "6"
    receiving_dfi_routing_number_padded = receiving_dfi_routing_number.ljust(9)
    dda_account_number_padded = dda_account_number.ljust(17)
    amount_padded = str(amount).zfill(10)
    individual_id_number_padded = individual_id_number.ljust(15)
    individual_name_padded = individual_name.ljust(22)
    trace_number = "00000001"
    
    return f"{record_type}{transaction_code}{receiving_dfi_routing_number_padded}{dda_account_number_padded}{amount_padded}{individual_id_number_padded}{individual_name_padded}{discretionary_data}{addenda_record_indicator}{trace_number}"

def create_batch_control(service_class_code, entry_count, total_debit_amount, total_credit_amount, company_identification, originating_dfi_id):
    """Creates a Batch Control record."""
    record_type = "8"
    message_authentication_code = "".ljust(19)
    originating_dfi_id_padded = originating_dfi_id.ljust(8)
    batch_number = "0001"

    return f"{record_type}{service_class_code}{str(entry_count).zfill(6)}{str(total_debit_amount).zfill(12)}{str(total_credit_amount).zfill(12)}{company_identification}{message_authentication_code}{originating_dfi_id_padded}{batch_number}"

def create_file_control(batch_count, block_count, entry_count, total_debit_amount, total_credit_amount, file_destination, file_origin):
    """Creates a File Control record."""
    record_type = "9"
    record_size = "094"
    blocking_factor = "10"
    format_code = "1"
    
    return f"{record_type}{str(batch_count).zfill(6)}{str(block_count).zfill(6)}{str(entry_count).zfill(8)}{str(total_debit_amount).zfill(12)}{str(total_credit_amount).zfill(12)}{file_destination.ljust(10)}{file_origin.ljust(10)}{record_size}{blocking_factor}{format_code}"

# Example Usage
file_header_record = create_file_header(destination_routing="123456789", origin_routing="987654321", destination_name="BANK OF AMERICA", origin_name="YOUR COMPANY")
batch_header_record = create_batch_header(service_class_code="200", company_name="YOUR COMPANY", company_identification="123456789", standard_entry_class_code="PPD", company_entry_description="PAYROLL", originating_dfi_id="98765432")

entries_data = [
    create_entry_detail(transaction_code="22", receiving_dfi_routing_number="111111111", dda_account_number="123456789012345", amount=10000, individual_id_number="EMP123", individual_name="John Doe", discretionary_data="", addenda_record_indicator="0"),
    create_entry_detail(transaction_code="27", receiving_dfi_routing_number="222222222", dda_account_number="987654321098765", amount=5000, individual_id_number="EMP456", individual_name="Jane Smith", discretionary_data="", addenda_record_indicator="0")
]

batch_control_record = create_batch_control(service_class_code="200", entry_count=len(entries_data), total_debit_amount="0", total_credit_amount="15000", company_identification="123456789", originating_dfi_id="98765432")
file_control_record = create_file_control(batch_count="1", block_count="1", entry_count=len(entries_data), total_debit_amount="0", total_credit_amount="15000", file_destination="123456789 ", file_origin="987654321 ")

ach_file_content = generate_ach_file(file_header_record, batch_header_record, entries_data, batch_control_record, file_control_record)

print(ach_file_content)

# To save to a file:
with open("my_ach_file.txt", "w") as file:
    file.write(ach_file_content)