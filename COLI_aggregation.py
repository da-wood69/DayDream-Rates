def cost_of_living_index(GI, RI, PPI, 
                         mu_GI=100, mu_RI=100, mu_PPI=100, mu_COLI=1.0, 
                         w_GI=0.4, w_RI=0.3, w_PPI=0.3, alpha=0.7):
    """
    Compute aggregated Cost of Living Index (COLI) using
    Groceries Index (GI), Restaurant Index (RI), and Purchasing Power Index (PPI).
    
    Parameters:
        GI (float): Groceries Index
        RI (float): Restaurant Index
        PPI (float): Local Purchasing Power Index
        mu_GI, mu_RI, mu_PPI (float): Reference averages for normalization
        mu_COLI (float): Reference average for scaling COLI* (default=1.0 means no rescaling)
        w_GI, w_RI, w_PPI (float): Weights for GI, RI, and PPI
        alpha (float): Sensitivity factor for PPI adjustment (0.5–1.0 is reasonable)
    
    Returns:
        float: Normalized and rescaled COLI*
    """

    GI_norm = GI / mu_GI
    RI_norm = RI / mu_RI
    PPI_norm = PPI / mu_PPI
    ECF = 1 / (1 + alpha * (PPI_norm - 1))
    COLI = (w_GI * GI_norm + w_RI * RI_norm) * ECF + w_PPI * PPI_norm
    COLI_star = 100 * (COLI / mu_COLI)

    return COLI_star

if __name__ == "__main__":
    GI = 120
    RI = 90
    PPI = 80

    result = cost_of_living_index(GI, RI, PPI, mu_GI=100, mu_RI=100, mu_PPI=100, mu_COLI=1.0)
    print(f"Aggregated Cost of Living Index (COLI*): {result:.2f}")
