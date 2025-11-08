import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd


st.markdown("""
    <style>
    /* Giảm độ rộng selectbox */
    div[data-baseweb="select"] {
        width: 150px !important;  /* đổi số px tùy ý */
    }
    </style>
    """, unsafe_allow_html=True)



# 1. Sidebar menu
with st.sidebar:    
    # Create the layout with columns
    col1, col2 = st.columns([3, 1])  # Adjust the ratio to your preference

    # Display the option menu in the first column
   
    selected = option_menu("Supply Chain Analysis", 
                        ["Production Planning Optimization"], 
                        icons=['gear'],  
                        menu_icon="cast", 
                        default_index=0)

    # Display the image in the second column if the option is selected

    if selected == "Production Planning Optimization":
        st.image("logo.jpg", caption="", use_container_width=False,width=400)

st.markdown("</div></div>", unsafe_allow_html=True)

# 2. Sub-menu for "Supply Chain Optimization"
if selected == "Production Planning Optimization":
    

    sub_selected = option_menu("Tối ưu kế hoạch sản xuất", 
                               ["Hướng dẫn", "Phân tích"], 
                               icons=['arrow-right-circle', 'gear'], 
                               menu_icon="cast", 
                               default_index=0,
                               orientation="horizontal")  # Make submenu horizontal
    
    if sub_selected == "Hướng dẫn":
       

        # Hiển thị nội dung hướng dẫn
        st.subheader("Bước 1: Tải Dữ Liệu")
        st.image("Buoc1.png", caption="", use_container_width=True)
     
        
        st.subheader("Bước 2: Chọn Đơn Vị Tính, Chọn Kỳ")
        st.image("Buoc2.png", caption="", use_container_width=False,width=450)
        st.image("Buoc3.png", caption="", use_container_width=False,width=150)
        st.image("Buoc4.png", caption="", use_container_width=False,width=800)
        
        st.subheader("Bước 3: Chọn các chức năng cụ thể để xem kết quả")
        st.image("Buoc5.png", caption="", use_container_width=False,width=800)
       
        
    elif sub_selected == "Phân tích":
   

        st.write("⬆️ Upload file data")
        # Tạo nút upload file
        uploaded_file = st.file_uploader("", type=["csv", "txt", "xlsx"])

        # Nếu người dùng đã upload file
        if uploaded_file is not None:
            # Xử lý các định dạng khác nhau
            try:
                if uploaded_file.name.endswith(".csv"):
                    df = pd.read_csv(uploaded_file)
                elif uploaded_file.name.endswith(".txt"):
                    df = pd.read_csv(uploaded_file, delimiter="\t")
                elif uploaded_file.name.endswith(".xlsx"):
                    df = pd.read_excel(uploaded_file)
                else:
                    st.error("Định dạng file không được hỗ trợ.")
                    st.stop()

                # Hiển thị bảng
                st.success("Tải dữ liệu thành công!")
                st.dataframe(df,height=200)


            except Exception as e:
                st.error(f"Lỗi khi đọc file: {e}")

            

        col1, col2, col3 = st.columns(3)
        with col1:
            st.write("📦 Chọn đơn vị")
            
        with col3:
            st.write("📅 Chọn kỳ")

        col11, col12,col13 =st.columns(3)

        with col11:
            # Radio buttons
            option = st.radio("",
                ("Units", "Cartons", "Pallets", "Tons", "Cbm"),
                index=0,  # chọn "Units" làm mặc định
                horizontal=True # hiển thị theo hàng ngang như hình"
            )
        with col13:
            time_period = st.selectbox(
                "",
                ("Ngày", "Tuần", "Tháng", "Năm"),
                index=2
            )
        
        col111, col112,col113 =st.columns(3)

        with col111:
            st.write("Đơn vị tiền tệ (VND/US/..vv)")
            symbol = st.text_input("Ký hiệu", value="VND", label_visibility="collapsed")
        with col112:
            st.write("Setup Costs (Chi phí thiết lập)")
            price = st.number_input("Giá", value=500, step=1, label_visibility="collapsed")
        with col113:
            st.write("Holding Cost (Chi phí lưu kho)")
            quantity = st.number_input("Số lượng", value=1, step=1, label_visibility="collapsed")

        sub_selected = option_menu("Kết quả tối ưu", 
                               ["Demand Forecasts", "Production Planning","Production Costs"], 
                               icons=['arrow-right-circle', 'gear'], 
                               menu_icon="cast", 
                               default_index=0,
                               orientation="horizontal")  # Make submenu horizontal
        
        

        # 1) Kiểm tra dữ liệu đã tải (giữ nguyên tên cột: 'Kỳ', 'Lượng dự báo')
        # ==== CHUẨN BỊ DỮ LIỆU & TỐI ƯU (chạy 1 lần, dùng cho cả 3 tab) ====
        if 'df' not in locals():
            st.info("Vui lòng tải file dữ liệu (cần đúng 2 cột: 'Kỳ' và 'Lượng dự báo').")
            st.stop()

        if not {"Kỳ", "Lượng dự báo"}.issubset(set(df.columns)):
            st.error("File dữ liệu cần có đúng 2 cột: 'Kỳ' và 'Lượng dự báo'.")
            st.stop()

        # Chuẩn hóa mà KHÔNG đổi tên cột
        data = df.copy()
        data["Kỳ"] = pd.to_numeric(data["Kỳ"], errors="coerce")
        data["Lượng dự báo"] = pd.to_numeric(data["Lượng dự báo"], errors="coerce")
        data = data.dropna(subset=["Kỳ", "Lượng dự báo"]).sort_values("Kỳ").reset_index(drop=True)

        if data.empty:
            st.error("Dữ liệu trống sau khi chuẩn hóa.")
            st.stop()

        # Lấy tham số từ UI
        unit_selected = option
        period_selected = time_period
        currency_symbol = symbol
        setup_cost = float(price)      # Setup cost
        hold_cost  = float(quantity)   # Holding cost / kỳ

        # ====== TÍNH TOÁN KẾ HOẠCH TỐI ƯU (Wagner-Whitin) ======
        data_calc = data.copy()
        max_period = int(data_calc["Kỳ"].max())

        # Tạo cột Order i
        for i in data_calc["Kỳ"].astype(int).unique():
            data_calc[f"Order {int(i)}"] = 0.0

        def forecast_at(k):
            v = data_calc.loc[data_calc["Kỳ"].astype(int) == int(k), "Lượng dự báo"]
            return float(v.values[0]) if len(v) else 0.0

        # Order 1
        order = 1
        for idx, row in data_calc.iterrows():
            current_period = int(row["Kỳ"])
            cost = setup_cost
            if current_period > 1:
                for t in range(1, current_period + 1):
                    cost += (t - 1) * forecast_at(t) * hold_cost
            data_calc.loc[idx, f"Order {order}"] = float(cost)

        # Order 2..max
        for order in range(2, max_period + 1):
            for idx, row in data_calc.iterrows():
                current_period = int(row["Kỳ"])
                if current_period >= order:
                    prev_row_index = data_calc.index[data_calc["Kỳ"].astype(int) == (order - 1)]
                    if len(prev_row_index):
                        prev_idx = prev_row_index[0]
                        values = list(data_calc.loc[prev_idx, [f"Order {i}" for i in range(1, order + 1)]].values)
                        positives = [v for v in values if v > 0]
                        best = min(positives) if positives else 0.0
                    else:
                        best = 0.0

                    cost = best + setup_cost
                    for t in range(order, current_period + 1):
                        cost += (t - order) * forecast_at(t) * hold_cost
                    data_calc.loc[idx, f"Order {order}"] = float(cost)

        # Truy vết ngược
        trace = data_calc.set_index("Kỳ").drop(["Lượng dự báo"], axis=1).T
        costs, initials, nexts, quantities_list = [], [], [], []
        i = max_period
        while i > 1:
            if i not in trace.columns:
                i -= 1
                continue
            col = trace[i]
            col = col[col > 0]
            if col.empty:
                i -= 1
                continue

            next_step = col.idxmin()         # 'Order k'
            cost = float(col.min())
            next_id = int(str(next_step).replace("Order ", ""))

            initial_step = i
            i = next_id - 1

            qty = data.loc[data["Kỳ"].astype(int).isin(range(next_id, initial_step + 1)), "Lượng dự báo"].sum()

            costs.append(cost)
            initials.append(initial_step)
            nexts.append(next_id)
            quantities_list.append(float(qty))

        df_results = pd.DataFrame({
            "backward": range(1, len(initials) + 1),
            "initial": initials,
            "nexts": nexts,
            "cost": costs,
            "quantity": quantities_list
        }).set_index("backward")

        total_cost_plan = df_results["cost"].sum() if not df_results.empty else 0.0

        # Bảng kết quả cuối
        results_final = data.copy()
        month_prod = df_results["nexts"].values if not df_results.empty else []
        prod_dict = dict(zip(month_prod, df_results["quantity"].values)) if len(month_prod) else {}
        results_final["production"] = results_final["Kỳ"].astype(int).apply(lambda t: prod_dict[t] if t in prod_dict else 0.0)
        results_final["IOH"] = (results_final["production"] - results_final["Lượng dự báo"]).cumsum()
        results_final["Holding Cost"] = (results_final["IOH"] * hold_cost)
        results_final["Set-Up Costs"] = results_final["production"].apply(lambda x: setup_cost if x > 0 else 0.0)
        results_final["Total Cost"] = results_final[["Holding Cost", "Set-Up Costs"]].sum(axis=1)

        # Một số tổng hữu ích
        n_months = int(len(data))
        total_demand = float(data["Lượng dự báo"].sum())
        max_demand = float(data["Lượng dự báo"].max())
        n_batches = int(len(df_results))
        total_costs_sum = float(results_final["Total Cost"].sum())
        holding_sum = float(results_final["Holding Cost"].sum())
        setup_sum = float(results_final["Set-Up Costs"].sum())

        # ====== HIỂN THỊ THEO 3 TAB ======
        import matplotlib.pyplot as plt
        import plotly.graph_objects as go
        import plotly.express as px

        plt.rcParams.update({"axes.grid": True})

        if sub_selected == "Demand Forecasts":
            st.subheader("📈 Demand Forecasts")

            # Hiển thị các thông số (Số kỳ, Tổng nhu cầu, Nhu cầu tối đa)
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("Number of Periods", f"{len(data)}")
            with c2:
                st.metric(f"Total Demand ({unit_selected})", f"{data['Lượng dự báo'].sum():,.0f}")
            with c3:
                st.metric(f"Maximum Demand ({unit_selected})", f"{data['Lượng dự báo'].max():,.0f}")

            # Tạo biểu đồ thanh với Plotly
            fig = go.Figure()

            fig.add_trace(go.Bar(
                x=results_final["Kỳ"].astype(int),
                y=results_final["Lượng dự báo"],
                text=results_final["Lượng dự báo"],  # Hiển thị giá trị trên mỗi cột
                textposition='auto',  # Đặt vị trí văn bản tự động
                marker=dict(color='lightblue', line=dict(color='black', width=1))  # Tùy chỉnh màu sắc và viền
            ))

            # Cập nhật các yếu tố của biểu đồ
            fig.update_layout(
                title="Demand Forecast",
                xaxis_title=f"Forecast Period ({period_selected})",
                yaxis_title=f"Demand Value ({unit_selected})",
                template="plotly_white",  # Chọn theme sáng
                hovermode="closest"  # Tạo hover effect khi di chuột
            )

            # Hiển thị biểu đồ tương tác
            st.plotly_chart(fig)

   


        elif sub_selected == "Production Planning":
            st.subheader("🏭 Production Planning")

            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("Production Batches", f"{n_batches}")
            with c2:
                st.metric(f"Total Demand ({unit_selected})", f"{total_demand:,.0f}")
            with c3:
                st.metric(f"Total Cost ({currency_symbol})", f"{total_costs_sum:,.0f}{currency_symbol}")

            # Biểu đồ: Forecast vs Production (bars kề nhau)
            x = results_final["Kỳ"].astype(int).values
            forecast = results_final["Lượng dự báo"].values
            production = results_final["production"].values
            width = 0.4  # độ rộng của cột

            # Tạo biểu đồ
            fig = go.Figure()

            # Thêm cột cho Lượng dự báo (forecast)
            fig.add_trace(go.Bar(
                x=x - width/2,
                y=forecast,
                width=width,
                name="forecast"
            ))

            # Thêm cột cho sản xuất (production)
            fig.add_trace(go.Bar(
                x=x + width/2,
                y=production,
                width=width,
                name="production"
            ))

            # Cập nhật các thông số của biểu đồ
            fig.update_layout(
                xaxis_title=period_selected if period_selected else "Period",
                yaxis_title=unit_selected,
                title="Production Plan",
                barmode='group',  # Các cột sẽ được hiển thị cạnh nhau
                legend_title="Legend"
            )

            # Hiển thị biểu đồ
            st.plotly_chart(fig)
            

        elif sub_selected == "Production Costs":
            st.subheader("💰 Production Costs")

            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric(f"Total Costs ({currency_symbol})", f"{total_costs_sum:,.0f}{currency_symbol}")
            with c2:
                st.metric(f"Holding Costs ({currency_symbol})", f"{holding_sum:,.0f}{currency_symbol}")
            with c3:
                st.metric(f"Setup Costs ({currency_symbol})", f"{setup_sum:,.0f}{currency_symbol}")

            # Biểu đồ: lũy kế Holding & Setup như ảnh (2 cột/period)
            # Assuming results_final is already defined
            costs_view = results_final.copy()
            costs_view["Holding Cumul"] = costs_view["Holding Cost"].cumsum()
            costs_view["Set-Up Cumul"] = costs_view["Set-Up Costs"].cumsum()

            # Extracting data for plotting
            x = costs_view["Kỳ"].astype(int).values
            holding_cumul = costs_view["Holding Cumul"].values
            setup_cumul = costs_view["Set-Up Cumul"].values
            currency_symbol = "$"  # Replace with your actual currency symbol
            period_selected = "Tháng"  # Replace with your actual period selection

            # Create Plotly figure
            fig = go.Figure()

            # Add bar traces for Holding Cumul and Set-Up Cumul
            fig.add_trace(go.Bar(
                x=x - 0.2, 
                y=holding_cumul, 
                width=0.4, 
                name="Holding Cumul"
            ))

            fig.add_trace(go.Bar(
                x=x + 0.2, 
                y=setup_cumul, 
                width=0.4, 
                name="Set-Up Cumul"
            ))

            # Update layout
            fig.update_layout(
                title="Production Costs",
                xaxis_title="Month" if period_selected == "Tháng" else period_selected,
                yaxis_title=currency_symbol,
                barmode='group',
                xaxis=dict(tickmode='linear'),
                template="plotly_white"
            )

            st.plotly_chart(fig)
            