from flask import Flask, request, jsonify, send_file
from fpdf import FPDF
from prettytable import PrettyTable
import matplotlib.pyplot as plt
import os

app = Flask(__name__)

# Define the directory to save PDFs
OUTPUT_DIR = os.path.join(os.getcwd(), 'output')
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.route('/generate_pdf', methods=['POST'])
def generate_pdf():
    try:
        data = request.json  # Get input from Wix site
        currency = data.get("currency", "$")

        # Extract inputs
        input_values = {label: float(data[label]) for label in data if label != "currency"}

        # Cost calculations
        Cost_op_at_full_load_SINGBATGPU = input_values["Price KW/h Electricity"] * input_values["Power Rating KVA"]
        Cost_op_at_full_load_DIESEL_GPU = input_values["Price ltr of Diesel"] * input_values["Ltr/h @ full load"]
        
        Cost_op_ta_SINGBATGPU = Cost_op_at_full_load_SINGBATGPU * input_values["Turn Around Transit Time (min)"] / 60
        Cost_op_ta_DIESEL_GPU = Cost_op_at_full_load_DIESEL_GPU * input_values["Turn Around Transit Time (min)"] / 60
        
        Yearly_ta = input_values["Number of Operations/Day"] * 365
        total_Cost_op_year_SINGBATGPU = Yearly_ta * Cost_op_ta_SINGBATGPU
        total_Cost_op_year_DIESEL_GPU = Yearly_ta * Cost_op_ta_DIESEL_GPU
        
        In_co_SINEBATGPU = input_values["SINEBAT GPU Price"] * input_values["Number of GPUs"] + total_Cost_op_year_SINGBATGPU
        In_co_DIESEL_GPU = input_values["Diesel GPU Price"] * input_values["Number of GPUs"] + total_Cost_op_year_DIESEL_GPU

        # Generate PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Cost Calculation Report", ln=True, align='C')

        # Add calculation results to PDF
        results_text = (
            f"Operational cost at full load SINEBATGPU: {Cost_op_at_full_load_SINGBATGPU:.2f} {currency}\n"
            f"Operational cost at full load DIESEL GPU: {Cost_op_at_full_load_DIESEL_GPU:.2f} {currency}\n"
            f"Total operational yearly cost SINEBATGPU: {total_Cost_op_year_SINGBATGPU:.2f} {currency}\n"
            f"Total operational yearly cost DIESEL GPU: {total_Cost_op_year_DIESEL_GPU:.2f} {currency}\n"
            f"Initial cost of SINEBATGPU: {In_co_SINEBATGPU:.2f} {currency}\n"
            f"Initial cost of DIESEL GPU: {In_co_DIESEL_GPU:.2f} {currency}"
        )
        pdf.multi_cell(0, 10, txt=results_text)

        pdf_path = os.path.join(OUTPUT_DIR, "cost_report.pdf")
        pdf.output(pdf_path)

        return send_file(pdf_path, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
